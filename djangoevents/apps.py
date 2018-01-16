from django.apps import AppConfig as BaseAppConfig
from django.conf import settings
from django.utils.module_loading import autodiscover_modules
from djangoevents import DomainEvent
from .exceptions import EventSchemaError
from .settings import adds_schema_version_to_event_data
from .schema import get_event_version
from .schema import load_all_event_schemas
import warnings


class AppConfig(BaseAppConfig):
    name = 'djangoevents'

    def ready(self):
        patch_domain_event()

        autodiscover_modules('handlers')
        autodiscover_modules('aggregates')

        # Once all handlers & aggregates are loaded we can import aggregate schema files.
        # `load_scheas()` assumes that all aggregates are imported at this point.
        load_schemas()


def get_app_module_names():
    return settings.INSTALLED_APPS


def load_schemas():
    """
    Try loading all the event schemas and complain loud if failure occurred.
    """
    try:
        load_all_event_schemas()
    except EventSchemaError as e:
        warnings.warn(str(e), UserWarning)


def patch_domain_event():
    """
    Patch `DomainEvent` to add `schema_version` to event payload.
    """

    old_init = DomainEvent.__init__

    def new_init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)

        if adds_schema_version_to_event_data():
            dct = self.__dict__
            key = 'schema_version'
            if key not in dct:
                dct[key] = get_event_version(self.__class__)

    DomainEvent.__init__ = new_init
