import warnings

from eventsourcing.domain.model.entity import DomainEvent
from eventsourcing.domain.model.entity import EventSourcedEntity


def abstract(cls):
    """
    Marks an aggregate/event class as abstract.

    Abstract aggregate/event provides (similarly do Django's abstract Models) means to share implementation
    details.
    """
    cls._abstract = True
    return cls


class BaseAggregate(EventSourcedEntity):
    """
    `EventSourcedEntity` with saner mutator routing & naming:

    >>> class Asset(BaseAggregate):
    >>>    class Created(BaseAggregate.Created):
    >>>        def mutate(event, klass):
    >>>            return klass(...)
    >>>
    >>>    class Updated(DomainEvent):
    >>>        def mutate(event, instance):
    >>>            instance.connect = True
    >>>            return instance
    """
    _abstract = False

    @classmethod
    def is_abstract_class(cls):
        return cls._abstract or cls is BaseAggregate

    @classmethod
    def mutate(cls, aggregate=None, event=None):
        if aggregate:
            aggregate._validate_originator(event)

        if not hasattr(event, 'mutate_event'):
            msg = "{} does not provide a mutate_event() method.".format(event.__class__)
            raise NotImplementedError(msg)

        aggregate = event.mutate_event(event, aggregate or cls)
        aggregate._increment_version()
        return aggregate

    @classmethod
    def create_for_event(cls, event):
        aggregate = cls(
            entity_id=event.entity_id,
            domain_event_id=event.domain_event_id,
            entity_version=event.entity_version,
        )
        return aggregate


class BaseEntity(BaseAggregate):
    """
    `EventSourcedEntity` with saner mutator routing:

    OBSOLETE! Interface kept for backward compatibility.
    """
    @classmethod
    def is_abstract_class(cls):
        return super().is_abstract_class() or cls is BaseEntity

    @classmethod
    def mutate(cls, entity=None, event=None):
        warnings.warn("`BaseEntity` is depreciated. Please switch to: `BaseAggregate`", DeprecationWarning)
        return super().mutate(aggregate=entity, event=event)
