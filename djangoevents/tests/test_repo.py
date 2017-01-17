from ..app import EventSourcingWithDjango
from ..models import Event
from ..repository import from_model_instance
from ..unifiedtranscoder import UnifiedStoredEvent
from eventsourcing.domain.model.entity import EventSourcedEntity
from eventsourcing.domain.services.transcoding import EntityVersion
from eventsourcing.utils.time import timestamp_from_uuid
from datetime import datetime
from django.db import transaction
from djangoevents.exceptions import AlreadyExists
import json
import pytest


class SampleAggregate(EventSourcedEntity):
    class Created(EventSourcedEntity.Created):
        pass


class SampleApp(EventSourcingWithDjango):
    def on_init(self):
        self.repo = self.get_repo_for_entity(SampleAggregate)


# uuid1 contains time
uuids = ['7ab23d4c-a520-11e6-80f5-76304dec7eb7',
         '846713a8-a520-11e6-80f5-76304dec7eb7',
         '917e42a0-a520-11e6-80f5-76304dec7eb7',
         '98ef1faa-a520-11e6-80f5-76304dec7eb7',
         '9e89b9de-a520-11e6-80f5-76304dec7eb7',
         'a678b7a8-a520-11e6-80f5-76304dec7eb7']


def new_stored_event(event_id, event_type, event_data, aggregate_id, aggregate_version):
    return UnifiedStoredEvent(
        event_id=event_id,
        event_type=event_type,
        event_data=json.dumps(event_data),
        aggregate_id=aggregate_id,
        aggregate_type='SampleAggregate',
        aggregate_version=aggregate_version,
        create_date=datetime.fromtimestamp(timestamp_from_uuid(event_id)),
        stored_entity_id='SampleAggregate::' + aggregate_id,
        metadata='',
        module_name='',
        class_name='',
    )


def save_events(repo, stored_events):
    for e in stored_events:
        repo.append(e)


@pytest.fixture
def repo():
    app = SampleApp()
    return app.stored_event_repo


@pytest.fixture
def stored_events():
    return [new_stored_event(uuids[i], 'Created', {'title': 'test'}, uuids[0], i) for i, uuid in enumerate(uuids)]


@pytest.mark.django_db
def test_repo_append(repo):
    test_stored_event = new_stored_event(uuids[0], 'Created', {'title': 'test'}, uuids[1], 1)

    # test basic save and get
    repo.append(test_stored_event)
    events = Event.objects.filter(stored_entity_id=test_stored_event.stored_entity_id)
    assert len(events) == 1
    assert test_stored_event == from_model_instance(events[0])

    # test unique constraint
    with transaction.atomic():
        test_stored_event2 = new_stored_event(uuids[2], 'Updated', {'title': 'updated test'}, uuids[1], 1)
        with pytest.raises(AlreadyExists):
            repo.append(test_stored_event2)

    # multiple saves
    test_stored_event3 = new_stored_event(uuids[2], 'Updated', {'title': 'updated test'}, uuids[1], 2)
    repo.append(test_stored_event3)
    events = Event.objects.filter(stored_entity_id=test_stored_event.stored_entity_id)
    assert len(events) == 2
    assert test_stored_event == from_model_instance(events[0])
    assert test_stored_event3 == from_model_instance(events[1])


@pytest.mark.django_db
def test_repo_get_entity_version(repo):
    test_stored_event = new_stored_event(uuids[0], 'Created', {'title': 'test'}, uuids[1], 1)
    repo.append(test_stored_event)
    entity_version = repo.get_entity_version(test_stored_event.stored_entity_id, 1)
    assert isinstance(entity_version, EntityVersion)
    assert entity_version.entity_version_id == 'SampleAggregate::' + uuids[1] + '::version::1'
    assert entity_version.event_id == uuids[0]


@pytest.mark.django_db
def test_repo_get_entity_events(repo, stored_events):
    save_events(repo, stored_events)

    # test get all
    retrieved_events = repo.get_entity_events(stored_events[0].stored_entity_id)
    assert retrieved_events == stored_events


@pytest.mark.django_db
def test_repo_get_entity_events_slicing(repo, stored_events):
    save_events(repo, stored_events)

    # test after
    retrieved_events = repo.get_entity_events(stored_events[0].stored_entity_id, after=stored_events[2].event_id)
    assert retrieved_events == stored_events[3:]

    # test until
    retrieved_events = repo.get_entity_events(stored_events[0].stored_entity_id, until=stored_events[2].event_id)
    assert retrieved_events == stored_events[:3]

    # test after + until
    retrieved_events = repo.get_entity_events(stored_events[0].stored_entity_id, after=stored_events[1].event_id,
                                              until=stored_events[4].event_id)
    assert retrieved_events == stored_events[2:5]

    # test limit
    retrieved_events = repo.get_entity_events(stored_events[0].stored_entity_id, limit=3)
    assert retrieved_events == stored_events[:3]


@pytest.mark.django_db
def test_repo_get_entity_events_ordering(repo, stored_events):
    save_events(repo, stored_events)

    # test query_ascending
    retrieved_events = repo.get_entity_events(stored_events[0].stored_entity_id, limit=3, query_ascending=False)
    assert retrieved_events == stored_events[-3:]

    # test results_ascending
    retrieved_events = repo.get_entity_events(stored_events[0].stored_entity_id, results_ascending=False)
    assert retrieved_events == stored_events[::-1]

    # test limit + query_ascending + results_ascending
    retrieved_events = repo.get_entity_events(stored_events[0].stored_entity_id, limit=3, query_ascending=False,
                                              results_ascending=False)
    assert retrieved_events == stored_events[-3:][::-1]

    # test after + until + query_ascending
    retrieved_events = repo.get_entity_events(stored_events[0].stored_entity_id, after=stored_events[1].event_id,
                                              until=stored_events[4].event_id, query_ascending=False)
    assert retrieved_events == stored_events[1:4]


@pytest.mark.django_db
def test_append_wrong_type(repo):
    # only allow UnifiedStoredEvent to be saved
    with transaction.atomic():
        with pytest.raises(AssertionError):
            repo.append('wrong object type')
