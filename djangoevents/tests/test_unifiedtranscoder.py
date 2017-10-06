import pytest
from ..unifiedtranscoder import UnifiedTranscoder
from eventsourcing.domain.model.entity import EventSourcedEntity
from django.core.serializers.json import DjangoJSONEncoder
from django.test.utils import override_settings
from unittest import mock


class SampleAggregate(EventSourcedEntity):
    class Created(EventSourcedEntity.Created):
        pass

    class Updated(EventSourcedEntity.AttributeChanged):
        event_type = 'overridden_event_type'


def override_schema_version_setting(adds):
    return override_settings(DJANGOEVENTS_CONFIG={
        'ADDS_SCHEMA_VERSION_TO_EVENT_DATA': adds,
    })


def test_serialize_and_deserialize_1():
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)
    # test serialize
    created = SampleAggregate.Created(entity_id='b089a0a6-e0b3-480d-9382-c47f99103b3d', attr1='val1', attr2='val2',
                                      metadata={'command_id': 123})
    created_stored_event = transcoder.serialize(created)
    assert created_stored_event.event_type == 'sample_aggregate_created'
    assert created_stored_event.event_version == 1
    assert created_stored_event.event_data == '{"attr1":"val1","attr2":"val2"}'
    assert created_stored_event.aggregate_id == 'b089a0a6-e0b3-480d-9382-c47f99103b3d'
    assert created_stored_event.aggregate_version == 0
    assert created_stored_event.aggregate_type == 'SampleAggregate'
    assert created_stored_event.module_name == 'djangoevents.tests.test_unifiedtranscoder'
    assert created_stored_event.class_name == 'SampleAggregate.Created'
    assert created_stored_event.metadata == '{"command_id":123}'
    # test deserialize
    created_copy = transcoder.deserialize(created_stored_event)
    assert 'metadata' not in created_copy.__dict__
    created.__dict__.pop('metadata')  # metadata is not included in deserialization
    assert created.__dict__ == created_copy.__dict__


def test_serialize_and_deserialize_2():
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)
    # test serialize
    updated = SampleAggregate.Updated(entity_id='b089a0a6-e0b3-480d-9382-c47f99103b3d', entity_version=10, attr1='val1',
                                      attr2='val2', metadata={'command_id': 123})
    updated_stored_event = transcoder.serialize(updated)
    assert updated_stored_event.event_type == 'overridden_event_type'
    assert updated_stored_event.event_version == 1
    assert updated_stored_event.event_data == '{"attr1":"val1","attr2":"val2"}'
    assert updated_stored_event.aggregate_id == 'b089a0a6-e0b3-480d-9382-c47f99103b3d'
    assert updated_stored_event.aggregate_version == 10
    assert updated_stored_event.aggregate_type == 'SampleAggregate'
    assert updated_stored_event.module_name == 'djangoevents.tests.test_unifiedtranscoder'
    assert updated_stored_event.class_name == 'SampleAggregate.Updated'
    assert updated_stored_event.metadata == '{"command_id":123}'
    # test deserialize
    updated_copy = transcoder.deserialize(updated_stored_event)
    assert 'metadata' not in updated_copy.__dict__
    updated.__dict__.pop('metadata') # metadata is not included in deserialization
    assert updated.__dict__ == updated_copy.__dict__


@override_schema_version_setting(adds=False)
def test_serializer_doesnt_include_schema_version_when_its_disabled():
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)
    event = SampleAggregate.Created(entity_id='b089a0a6-e0b3-480d-9382-c47f99103b3d', attr1='val1', attr2='val2')
    serialized_event = transcoder.serialize(event)
    assert serialized_event.event_data == '{"attr1":"val1","attr2":"val2"}'


@override_schema_version_setting(adds=True)
def test_serializer_includes_schema_version_when_its_enabled():
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)
    event = SampleAggregate.Created(entity_id='b089a0a6-e0b3-480d-9382-c47f99103b3d', attr1='val1', attr2='val2')
    serialized_event = transcoder.serialize(event)
    assert serialized_event.event_data == '{"attr1":"val1","attr2":"val2","schema_version":1}'


def test_deserializer_uses_none_as_schema_version_default():
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)

    with override_schema_version_setting(adds=False):
        event = SampleAggregate.Created(entity_id='123')

    serialized_event = transcoder.serialize(event)
    assert serialized_event.event_data == '{}'

    with override_schema_version_setting(adds=True):
        event = transcoder.deserialize(serialized_event)

    assert event.schema_version is None


def test_metadata_is_optional():
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)
    created = SampleAggregate.Created(entity_id='b089a0a6-e0b3-480d-9382-c47f99103b3d')

    try:
        transcoder.serialize(created)
    except AttributeError:
        pytest.fail('Serialization of an event without metadata should not raise an exception.')


def test_transcoder_passes_all_attributes_to_event_constructor():
    attributes = {
        'entity_id': 'b089a0a6-e0b3-480d-9382-c47f99103b3d',
        'foo': 0,
        'bar': 1,
    }

    event = SampleAggregate.Created(**attributes)
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)
    serialized_event = transcoder.serialize(event)

    init_call_args = None
    def init(self, *args, **kwargs):
        nonlocal init_call_args
        init_call_args = (args, kwargs)

    with mock.patch.object(SampleAggregate.Created, '__init__', init):
        transcoder.deserialize(serialized_event)

    args, kwargs = init_call_args
    assert args == tuple()

    for key, value in attributes.items():
        assert key in kwargs
        assert kwargs[key] == value
