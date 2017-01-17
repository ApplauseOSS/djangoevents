"""
Same as settings_test but instead of migration
uses provided sql. This is for test to make sure
that Event model works fine with db scheme
all teams agreed on.
"""
from .settings_test import *
import os


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ.get("MYSQL_HOSTNAME", '127.0.0.1'),
        'PORT': os.environ.get("MYSQL_PORT", 3306),
        'NAME': os.environ.get("MYSQL_DATABASE", 'djangoevents'),
        'USER': os.environ.get("MYSQL_USER", 'root'),
    }
}
