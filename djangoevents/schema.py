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


def load_event_schema(aggregate, event):
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
    def make_path(version):
        return _event_to_schema_path(aggregate_cls, event_cls, avro_dir, version)

    avro_dir = avro_dir or get_avro_dir()
    version = _get_schema_version(event_cls)

    if version:
        return make_path(version)
    else:
        # use 1 as the default version
        path = make_path(1)

        # look for schemas on disk and choose the one with the highest version
        for version in itertools.count(2):
            potential_path = make_path(version)
            if os.path.exists(potential_path):
                path = potential_path
            else:
                break

        return path


def _get_schema_version(event_cls):
    version = getattr(event_cls, 'schema_version', None)

    if version is None:
        return None
    else:
        try:
            return int(version)
        except ValueError:
            msg = "`{}.schema_version` must be an integer. Currently it is {}."
            raise EventSchemaError(msg.format(event_cls, event_cls.schema_version))


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
