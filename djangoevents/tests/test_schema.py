import avro.schema
from djangoevents.exceptions import EventSchemaError

import djangoevents.schema as schema
import json
import os
import pytest
import shutil
import tempfile

from djangoevents.domain import BaseAggregate
from djangoevents.domain import DomainEvent
from io import StringIO
from django.test import override_settings
from unittest import mock
from .test_domain import SampleEntity
from ..schema import set_event_version


class Project(BaseAggregate):
    class Created(BaseAggregate.Created):
        def mutate_event(self, event, klass):
            return klass(
                entity_id=event.entity_id,
                entity_version=event.entity_version,
                domain_event_id=event.domain_event_id,
                name=event.name,
            )

    class Closed(DomainEvent):
        # no mutate_event
        pass

    def __init__(self, project_id, name, **kwargs):
        super().__init__(**kwargs)
        self.project_id = project_id
        self.name = name


PROJECT_CREATED_SCHEMA = json.dumps({
    "name": "project_created",
    "type": "record",
    "doc": "Event posted when a project has been created",
    "namespace": "services.project_svc",
    "fields": [
        {
            "name": "entity_id",
            "type": "string",
            "doc": "ID of a the asset."
        },
        {
            "name": "entity_version",
            "type": "string",
            "doc": "Aggregate revision"
        },
        {
            "name": "domain_event_id",
            "type": "string",
            "doc": "ID of the last modifying event"
        },
        {
            "name": "name",
            "type": "string",
            "doc": "name of the project"
        }
    ]
})


@override_settings(BASE_DIR='/path/to/proj/src/')
@mock.patch.object(schema, 'list_concrete_aggregates', return_value=[Project])
@mock.patch.object(schema, 'load_event_schema')
def test_load_all_event_schemas(load_schema, load_aggs):
    schema.load_all_event_schemas()
    load_schema.assert_called_once_with(Project, Project.Created)


@override_settings(BASE_DIR='/path/to/proj/src/')
@mock.patch.object(schema, 'list_concrete_aggregates', return_value=[Project])
def test_load_all_event_schemas_missing_specs(list_aggs):
    with pytest.raises(EventSchemaError) as e:
        schema.load_all_event_schemas()

    path = "/path/to/proj/avro/project/v1_project_created.json"
    msg = "No event schema found for: {cls} (expecting file at:{path}).".format(cls=Project.Created, path=path)
    assert msg in str(e.value)


@override_settings(BASE_DIR='/path/to/proj/src/')
def test_valid_event_to_schema_path():
    SampleEntity.Created.version = None
    avro_path = schema.event_to_schema_path(aggregate_cls=SampleEntity, event_cls=SampleEntity.Created)
    assert avro_path == "/path/to/proj/avro/sample_entity/v1_sample_entity_created.json"


@override_settings(BASE_DIR='/path/to/proj/src/')
def test_event_to_schema_path_chooses_file_with_the_highest_version():
    try:
        # make temporary directory structure
        temp_dir = tempfile.mkdtemp()
        entity_dir = os.path.join(temp_dir, 'sample_entity')
        os.mkdir(entity_dir)

        for version in range(1, 4):
            # make empty schema file
            expected_schema_path = os.path.join(entity_dir, 'v{}_sample_entity_created.json'.format(version))
            with open(expected_schema_path, 'w'):
                pass

            # refresh version
            set_event_version(SampleEntity, SampleEntity.Created, avro_dir=temp_dir)

            # check path
            schema_path = schema.event_to_schema_path(
                aggregate_cls=SampleEntity,
                event_cls=SampleEntity.Created,
                avro_dir=temp_dir,
            )
            assert schema_path == expected_schema_path
    finally:
        # remove temporary directory
        shutil.rmtree(temp_dir)


def test_parse_invalid_event_schema():
    fp = StringIO("Invalid schema")

    with pytest.raises(avro.schema.SchemaParseException):
        schema.parse_event_schema(fp)


def test_parse_valid_event_schema():
    evt_schema = schema.parse_event_schema(PROJECT_CREATED_SCHEMA)
    assert evt_schema is not None


def test_validate_valid_event():
    class TestEvent:
        def __init__(self):
            self.entity_id = "1"
            self.entity_version = "XYZ"
            self.domain_event_id = "2"
            self.name = "Awesome Project"

    event = TestEvent()
    evt_schema = avro.schema.Parse(PROJECT_CREATED_SCHEMA)
    ret = schema.validate_event(event, evt_schema)
    assert ret is True


def test_validate_invalid_event():
    class TestEvent:
        def __init__(self):
            self.test = 'test'

    event = TestEvent()
    evt_schema = avro.schema.Parse(PROJECT_CREATED_SCHEMA)
    ret = schema.validate_event(event, evt_schema)
    assert ret is False


def test_decode_cls_name():
    class LongName:
        pass

    class Shortname:
        pass

    assert schema.decode_cls_name(LongName) == 'long_name'
    assert schema.decode_cls_name(Shortname) == 'shortname'
