from django.apps import AppConfig as BaseAppConfig
from django.conf import settings
from django.utils.module_loading import import_module
import os.path


class AppConfig(BaseAppConfig):
    name = 'djangoevents'

    def ready(self):
        for app_module_name in get_app_module_names():
            import_handlers_module(app_module_name)


def get_app_module_names():
    return settings.INSTALLED_APPS


def import_handlers_module(app_module_name):
    handlers_module_name = '%s.handlers' % app_module_name
    try:
        import_module(handlers_module_name)
    except ImportError:
        # we need to re-raise exception in case there was import errors inside
        # handlers.py module
        handlers_file_name = get_handlers_file_name(app_module_name)
        if os.path.exists(handlers_file_name):
            raise


def get_handlers_file_name(app_module_name):
    module = import_module(app_module_name)
    module_dir = os.path.dirname(module.__file__)
    return os.path.join(module_dir, 'handlers.py')
