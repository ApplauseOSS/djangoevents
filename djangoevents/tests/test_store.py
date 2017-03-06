import djangoevents
from unittest import mock


@mock.patch.object(djangoevents, 'is_validation_enabled', return_value=True)
@mock.patch.object(djangoevents, 'validate_event', return_value=True)
@mock.patch.object(djangoevents, 'es_publish', return_value=True)
def test_store_event_validation_enabled(publish, validate_event, validation_enabled):
    evt = {}
    djangoevents.store_event(evt)

    assert validation_enabled.call_count == 1
    assert validate_event.call_args_list == [mock.call(evt)]
    assert publish.call_args_list == [mock.call(evt)]


@mock.patch.object(djangoevents, 'is_validation_enabled', return_value=False)
@mock.patch.object(djangoevents, 'validate_event', return_value=True)
@mock.patch.object(djangoevents, 'es_publish', return_value=True)
def test_store_event_validation_disabled(publish, validate_event, validation_enabled):
    evt = {}
    djangoevents.store_event(evt)

    assert validation_enabled.call_count == 1
    assert validate_event.call_count == 0
    assert publish.call_args_list == [mock.call(evt)]


@mock.patch.object(djangoevents, 'is_validation_enabled', return_value=False)
@mock.patch.object(djangoevents, 'validate_event', return_value=True)
@mock.patch.object(djangoevents, 'es_publish', return_value=True)
def test_store_event_validation_disabled_force(publish, validate_event, validation_enabled):
    evt = {}
    djangoevents.store_event(evt, force_validate=True)

    assert validation_enabled.call_count == 1
    assert validate_event.call_args_list == [mock.call(evt)]
    assert publish.call_args_list == [mock.call(evt)]
