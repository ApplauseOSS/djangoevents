import warnings

from djangoevents.utils_abstract import abstract
from djangoevents.utils_abstract import is_abstract
from eventsourcing.domain.model.entity import DomainEvent
from eventsourcing.domain.model.entity import EventSourcedEntity


@abstract
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

    @classmethod
    def is_abstract_class(cls):
        return is_abstract(cls)

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
