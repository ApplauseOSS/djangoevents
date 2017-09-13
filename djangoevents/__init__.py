import warnings

from eventsourcing.domain.model.entity import EventSourcedEntity
from eventsourcing.domain.model.entity import entity_mutator
from eventsourcing.domain.model.entity import singledispatch
from eventsourcing.domain.model.decorators import subscribe_to
from eventsourcing.domain.model.events import publish as es_publish
from eventsourcing.domain.model.events import subscribe
from eventsourcing.domain.model.events import unsubscribe
from eventsourcing.infrastructure.event_sourced_repo import EventSourcedRepository
from .domain import BaseEntity
from .domain import BaseAggregate
from .domain import DomainEvent
from .app import EventSourcingWithDjango
from .exceptions import EventSchemaError
from .schema import validate_event
from .settings import is_validation_enabled

default_app_config = 'djangoevents.apps.AppConfig'

__all__ = [
    'DomainEvent',
    'EventSourcedEntity',
    'EventSourcedRepository',
    'entity_mutator',
    'singledispatch',
    'publish',
    'store_event'
    'subscribe',
    'unsubscribe',
    'subscribe_to',
    'BaseEntity',
    'BaseAggregate',
    'EventSourcingWithDjango'
]


def publish(event):
    warnings.warn("`publish` is depreciated. Please switch to: `store_event`.", DeprecationWarning)
    return es_publish(event)


def store_event(event, force_validate=False):
    """
    Store an event to the service's event journal. Optionally validates event
    schema if one is provided.

    `force_validate` - enforces event schema validation even if configuration disables it globally.
    """
    if is_validation_enabled() or force_validate:
        is_valid = validate_event(event)
        if not is_valid:
            msg = "Event: {} does not match its schema.".format(event)
            raise EventSchemaError(msg)

    return es_publish(event)
