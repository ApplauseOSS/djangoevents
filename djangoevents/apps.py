from django.apps import AppConfig as BaseAppConfig
from django.conf import settings
from django.utils.module_loading import import_module
from djangoevents import DomainEvent
from .exceptions import EventSchemaError
from .settings import adds_schema_version_to_event_data
from .schema import get_event_version
from .schema import load_all_event_schemas
import os.path
import warnings


class AppConfig(BaseAppConfig):
    name = 'djangoevents'

    def ready(self):
        patch_domain_event()

        for app_module_name in get_app_module_names():
            import_handlers_module(app_module_name)
            import_aggregates_module(app_module_name)

        # Once all handlers & aggregates are loaded we can import aggregate schema files.
        # `load_scheas()` assumes that all aggregates are imported at this point.
        load_schemas()


def get_app_module_names():
    return settings.INSTALLED_APPS


def import_handlers_module(app_module_name):
    return import_app_module(app_module_name, 'handlers')


def import_aggregates_module(app_module_name):
    return import_app_module(app_module_name, 'aggregates')


def import_app_module(app_module_name, module_name):
    full_module_name = '%s.%s' % (app_module_name, module_name)
    try:
        import_module(full_module_name)
    except ImportError:
        # we need to re-raise exception in case there was import error inside
        # `module_name` module
        module_file_name = get_module_file_name(app_module_name, module_name)
        if os.path.exists(module_file_name):
            raise

def get_module_file_name(app_module_name, module_name):
    module = import_module(app_module_name)
    module_dir = os.path.dirname(module.__file__)
    return os.path.join(module_dir, '%s.py' % module_name)


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
            self.__dict__['schema_version'] = get_event_version(self.__class__)

    DomainEvent.__init__ = new_init
