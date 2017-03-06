import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


_DEFAULTS = {
    'EVENT_SCHEMA_VALIDATION': {
        'ENABLED': False,
        'SCHEMA_DIR': 'avro',
    },
}

# library user must be able to override the defaults.
CONFIG = getattr(settings, 'DJANGOEVENTS_CONFIG', _DEFAULTS)


def is_validation_enabled():
    return CONFIG.get('EVENT_SCHEMA_VALIDATION', {}).get('ENABLED', False)


def get_avro_dir():
    try:
        avro_folder = CONFIG.get('EVENT_SCHEMA_VALIDATION', {})['SCHEMA_DIR']
    except KeyError:
        raise ImproperlyConfigured("Please define `SCHEMA_DIR`")

    avro_dir = os.path.abspath(os.path.join(settings.BASE_DIR, '..', avro_folder))
    return avro_dir
