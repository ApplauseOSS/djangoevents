from .unifiedtranscoder import UnifiedStoredEvent
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone
from djangoevents.exceptions import AlreadyExists
from eventsourcing.domain.services.eventstore import AbstractStoredEventRepository
from eventsourcing.domain.services.eventstore import EntityVersionDoesNotExist
from eventsourcing.domain.services.transcoding import EntityVersion
from eventsourcing.utils.time import timestamp_from_uuid
import datetime


class DjangoStoredEventRepository(AbstractStoredEventRepository):

    def __init__(self, *args, **kwargs):
        from .models import Event  # import model at runtime for making top level import possible
        self.EventModel = Event
        super(DjangoStoredEventRepository, self).__init__(*args, **kwargs)

    def append(self, new_stored_event, new_version_number=None, max_retries=3, artificial_failure_rate=0):
        """
        Saves given stored event in this repository.
        """
        # Check the new event is a stored event instance.
        assert isinstance(new_stored_event, UnifiedStoredEvent)

        # Not calling validate_expected_version!

        # Write the event.
        self.write_version_and_event(
            new_stored_event=new_stored_event,
            new_version_number=new_version_number,
            max_retries=max_retries,
            artificial_failure_rate=artificial_failure_rate,
        )

    def get_entity_version(self, stored_entity_id, version_number):
        events_query = self.EventModel.objects.filter(stored_entity_id=stored_entity_id)\
            .filter(aggregate_version=version_number)
        if not events_query.exists():
            raise EntityVersionDoesNotExist()

        return EntityVersion(
            entity_version_id=self.make_entity_version_id(stored_entity_id, version_number),
            event_id=events_query[0].event_id,
        )

    def write_version_and_event(self, new_stored_event, new_version_number=None, max_retries=3,
                                artificial_failure_rate=0):
        try:
            self.EventModel.objects.create(
                event_id=new_stored_event.event_id,
                event_type=new_stored_event.event_type,
                event_data=new_stored_event.event_data,
                aggregate_id=new_stored_event.aggregate_id,
                aggregate_type=new_stored_event.aggregate_type,
                aggregate_version=new_stored_event.aggregate_version,
                create_date=make_aware_if_needed(new_stored_event.create_date),
                metadata=new_stored_event.metadata,
                module_name=new_stored_event.module_name,
                class_name=new_stored_event.class_name,
                stored_entity_id=new_stored_event.stored_entity_id,
            )
        except IntegrityError as err:
            create_attempt = not new_version_number
            if create_attempt:
                msg = "Aggregate with id %r already exists" % new_stored_event.aggregate_id
                raise AlreadyExists(msg)
            else:
                raise err

    def get_entity_events(self, stored_entity_id, after=None, until=None, limit=None, query_ascending=True,
                          results_ascending=True):
        events = self.EventModel.objects.filter(stored_entity_id=stored_entity_id)
        if query_ascending:
            events = events.order_by('id')
        else:
            events = events.order_by('-id')

        if after is not None:
            after_ts = datetime.datetime.fromtimestamp(timestamp_from_uuid(after))
            if query_ascending:
                events = events.filter(create_date__gt=after_ts)
            else:
                events = events.filter(create_date__gte=after_ts)

        if until is not None:
            until_ts = datetime.datetime.fromtimestamp(timestamp_from_uuid(until))
            if query_ascending:
                events = events.filter(create_date__lte=until_ts)
            else:
                events = events.filter(create_date__lt=until_ts)

        if limit is not None:
            events = events[:limit]

        events = list(events)
        if results_ascending != query_ascending:
            events.reverse()
        return [from_model_instance(e) for e in events]


def from_model_instance(event):
    return UnifiedStoredEvent(
        event_id=event.event_id,
        event_type=event.event_type,
        event_data=event.event_data,
        aggregate_id=event.aggregate_id,
        aggregate_type=event.aggregate_type,
        aggregate_version=event.aggregate_version,
        create_date=event.create_date,
        metadata=event.metadata,
        module_name=event.module_name,
        class_name=event.class_name,
        stored_entity_id=event.stored_entity_id
    )


def make_aware_if_needed(dt):
    if settings.USE_TZ:
        return timezone.make_aware(dt)
    else:
        return dt
