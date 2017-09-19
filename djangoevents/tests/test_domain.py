from ..domain import BaseEntity, DomainEvent
from ..schema import get_event_version
from ..schema import set_event_version
from django.test import override_settings
from unittest import mock

import os
import pytest


class SampleEntity(BaseEntity):
    class Created(BaseEntity.Created):
        def mutate_event(self, event, klass):
            return klass(entity_id=event.entity_id,
                         entity_version=event.entity_version,
                         domain_event_id=event.domain_event_id)

    class Updated(DomainEvent):
        def mutate_event(self, event, entity):
            entity.is_dirty = True
            return entity

    class Closed(DomainEvent):
        # no mutate_event
        pass

    def __init__(self, is_dirty=False, **kwargs):
        super().__init__(**kwargs)
        self.is_dirty = is_dirty


def test_base_entity_calls_mutator():
    create_event = SampleEntity.Created(entity_id=1)
    entity = SampleEntity.mutate(event=create_event)

    close_event = SampleEntity.Updated(entity_id=entity.id, entity_version=entity.version)
    entity = SampleEntity.mutate(event=close_event, entity=entity)
    assert entity.is_dirty is True


def test_base_entity_requires_mutator():
    create_event = SampleEntity.Created(entity_id=1)
    entity = SampleEntity.mutate(event=create_event)

    close_event = SampleEntity.Closed(entity_id=entity.id, entity_version=entity.version)

    with pytest.raises(NotImplementedError):
        SampleEntity.mutate(event=close_event, entity=entity)


def test_create_for_event():
    event = SampleEntity.Created(
        entity_id='ENTITY_ID',
        domain_event_id='DOMAIN_EVENT_ID',
        entity_version=0,
    )
    obj = SampleEntity.create_for_event(event)

    assert obj.id == 'ENTITY_ID'
    assert obj.version == 0


@override_settings(BASE_DIR='/path/to/proj/src/')
def test_version_1():
    assert get_event_version(SampleEntity.Created) == 1


def test_version_4(tmpdir):
    # make temporary directory structure
    avro_dir = tmpdir.mkdir('avro_dir')
    entity_dir = avro_dir.mkdir('sample_entity')

    original_version = getattr(SampleEntity.Created, 'version', None)
    try:
        for version in range(1, 4):
            # make empty schema file
            expected_schema_path = os.path.join(entity_dir.strpath, 'v{}_sample_entity_created.json'.format(version))
            with open(expected_schema_path, 'w'):
                pass

            # refresh version
            set_event_version(SampleEntity, SampleEntity.Created, avro_dir=avro_dir.strpath)

            assert get_event_version(SampleEntity.Created) == version
    finally:
        SampleEntity.Created.version = original_version


@override_settings(DJANGOEVENTS_CONFIG={
    'ADDS_SCHEMA_VERSION_TO_EVENT_DATA': False,
})
def test_events_dont_have_schema_version_when_disabled():
    event = SampleEntity.Created(entity_id=1)
    assert not hasattr(event, 'schema_version')


@override_settings(DJANGOEVENTS_CONFIG={
    'ADDS_SCHEMA_VERSION_TO_EVENT_DATA': True,
})
def test_events_have_schema_version_when_enabled():
    event = SampleEntity.Created(entity_id=1)
    assert event.schema_version == 1


@override_settings(DJANGOEVENTS_CONFIG={
    'ADDS_SCHEMA_VERSION_TO_EVENT_DATA': True,
})
def test_events_have_correct_schema_version():

    with mock.patch.object(SampleEntity.Created, 'version', 666):
        event = SampleEntity.Created(entity_id=1)
        assert event.schema_version == 666
