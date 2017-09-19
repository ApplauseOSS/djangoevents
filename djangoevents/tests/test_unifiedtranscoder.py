import pytest
from ..unifiedtranscoder import UnifiedTranscoder
from eventsourcing.domain.model.entity import EventSourcedEntity
from django.core.serializers.json import DjangoJSONEncoder
from django.test.utils import override_settings


class SampleAggregate(EventSourcedEntity):
    class Created(EventSourcedEntity.Created):
        pass

    class Updated(EventSourcedEntity.AttributeChanged):
        event_type = 'overridden_event_type'


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


@override_settings(DJANGOEVENTS_CONFIG={
    'ADDS_SCHEMA_VERSION_TO_EVENT_DATA': False,
})
def test_serializer_doesnt_include_schema_version_when_its_disabled():
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)
    event = SampleAggregate.Created(entity_id='b089a0a6-e0b3-480d-9382-c47f99103b3d', attr1='val1', attr2='val2')
    serialized_event = transcoder.serialize(event)
    assert serialized_event.event_data == '{"attr1":"val1","attr2":"val2"}'


@override_settings(DJANGOEVENTS_CONFIG={
    'ADDS_SCHEMA_VERSION_TO_EVENT_DATA': True,
})
def test_serializer_includes_schema_version_when_its_enabled():
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)
    event = SampleAggregate.Created(entity_id='b089a0a6-e0b3-480d-9382-c47f99103b3d', attr1='val1', attr2='val2')
    serialized_event = transcoder.serialize(event)
    assert serialized_event.event_data == '{"attr1":"val1","attr2":"val2","schema_version":1}'


def test_metadata_is_optional():
    transcoder = UnifiedTranscoder(json_encoder_cls=DjangoJSONEncoder)
    created = SampleAggregate.Created(entity_id='b089a0a6-e0b3-480d-9382-c47f99103b3d')

    try:
        transcoder.serialize(created)
    except AttributeError:
        pytest.fail('Serialization of an event without metadata should not raise an exception.')
