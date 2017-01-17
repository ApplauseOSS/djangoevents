from eventsourcing.domain.model.entity import DomainEvent
from eventsourcing.domain.model.entity import EventSourcedEntity


class BaseEntity(EventSourcedEntity):
    """
    `EventSourcedEntity` with saner mutator routing:

    >>> class Asset(BaseEntity):
    >>>    class Created(BaseEntity.Created):
    >>>        def mutate(event, klass):
    >>>            return klass(...)
    >>>
    >>>    class Updated(DomainEvent):
    >>>        def mutate(event, instance):
    >>>            instance.connect = True
    >>>            return instance
    """
    @classmethod
    def mutate(cls, entity=None, event=None):
        if entity:
            entity._validate_originator(event)

        if not hasattr(event, 'mutate_event'):
            msg = "{} does not provide a mutate_event() method.".format(event.__class__)
            raise NotImplementedError(msg)

        entity = event.mutate_event(event, entity or cls)
        entity._increment_version()
        return entity

    @classmethod
    def create_for_event(cls, event):
        entity = cls(
            entity_id=event.entity_id,
            domain_event_id=event.domain_event_id,
            entity_version=event.entity_version,
        )
        return entity
