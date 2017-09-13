"""
Aggregate event avro schema validation
"""

import avro.schema
import itertools
import os
import stringcase

from avro.io import Validate as avro_validate
from .settings import get_avro_dir
from .utils import list_concrete_aggregates
from .utils import list_aggregate_events
from .utils import event_to_json
from .exceptions import EventSchemaError


schemas = {}


def load_all_event_schemas():
    """
    Initializes aggregate event schemas lookup cache.
    """
    errors = []
    for aggregate in list_concrete_aggregates():
        for event in list_aggregate_events(aggregate_cls=aggregate):
            try:
                schemas[event] = load_event_schema(aggregate, event)
            except EventSchemaError as e:
                errors.append(str(e))

    # Serve all schema errors at once not iteratively.
    if errors:
        raise EventSchemaError("\n".join(errors))

    return schemas


def set_event_version(aggregate_cls, event_cls, avro_dir=None):
    avro_dir = avro_dir or get_avro_dir()
    event_cls.version = _find_highest_event_version_based_on_schemas(aggregate_cls, event_cls, avro_dir)


def get_event_version(event_cls):
    return getattr(event_cls, 'version', None) or 1


def load_event_schema(aggregate, event):
    set_event_version(aggregate, event)
    spec_path = event_to_schema_path(aggregate, event)

    try:
        with open(spec_path) as fp:
            return parse_event_schema(fp.read())
    except FileNotFoundError:
        msg = "No event schema found for: {event} (expecting file at:{path})."
        raise EventSchemaError(msg.format(event=event, path=spec_path))
    except avro.schema.SchemaParseException as e:
        msg = "Can't parse schema for event: {event} from {path}."
        raise EventSchemaError(msg.format(event=event, path=spec_path)) from e


def event_to_schema_path(aggregate_cls, event_cls, avro_dir=None):
    avro_dir = avro_dir or get_avro_dir()
    version = get_event_version(event_cls)
    return _event_to_schema_path(aggregate_cls, event_cls, avro_dir, version)


def _find_highest_event_version_based_on_schemas(aggregate_cls, event_cls, avro_dir):
    version = None
    for version_candidate in itertools.count(1):
        schema_path = _event_to_schema_path(aggregate_cls, event_cls, avro_dir, version_candidate)
        if os.path.exists(schema_path):
            version = version_candidate
        else:
            break

    return version


def _event_to_schema_path(aggregate_cls, event_cls, avro_dir, version):
    aggregate_name = decode_cls_name(aggregate_cls)
    event_name = decode_cls_name(event_cls)

    filename = "v{version}_{aggregate_name}_{event_name}.json".format(
        aggregate_name=aggregate_name, event_name=event_name, version=version)

    return os.path.join(avro_dir, aggregate_name, filename)


def decode_cls_name(cls):
    """
    Convert camel case class name to snake case names used in event documentation.
    """
    return stringcase.snakecase(cls.__name__)


def parse_event_schema(spec_body):
    schema = avro.schema.Parse(spec_body)
    return schema


def get_schema_for_event(event_cls):
    if event_cls not in schemas:
        raise EventSchemaError("Cached Schema not found for: {}".format(event_cls))
    return schemas[event_cls]


def validate_event(event, schema=None):
    schema = schema or get_schema_for_event(event.__class__)
    return avro_validate(schema, event_to_json(event))
