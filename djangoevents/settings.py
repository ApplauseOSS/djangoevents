import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


_DEFAULTS = {
    'EVENT_SCHEMA_VALIDATION': {
        'ENABLED': False,
        'SCHEMA_DIR': 'avro',
    },
    'EVENT_TRANSCODER': {
        'ADDS_EVENT_VERSION_TO_DATA': False,
    },
}


def get_config():
    """
    Function getting djangoevents configuration defined in Django settings.
    We use a function because Django settings can be mutable (useful for example in tests).
    """
    return getattr(settings, 'DJANGOEVENTS_CONFIG', _DEFAULTS)


def is_validation_enabled():
    config = get_config()
    return config.get('EVENT_SCHEMA_VALIDATION', {}).get('ENABLED', False)


def get_avro_dir():
    config = get_config()

    try:
        avro_folder = config.get('EVENT_SCHEMA_VALIDATION', {})['SCHEMA_DIR']
    except KeyError:
        raise ImproperlyConfigured("Please define `SCHEMA_DIR`")

    avro_dir = os.path.abspath(os.path.join(settings.BASE_DIR, '..', avro_folder))
    return avro_dir


def transcoder_adds_event_version_to_data():
    config = get_config()
    return config.get('EVENT_TRANSCODER', {}).get('ADDS_EVENT_VERSION_TO_DATA', False)
