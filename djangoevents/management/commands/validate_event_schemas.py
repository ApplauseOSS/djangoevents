"""
Parses event schemas and reports on their validity.
"""
from django.core.management.base import BaseCommand
from djangoevents.exceptions import EventSchemaError
from djangoevents.schema import load_all_event_schemas, schemas
from djangoevents.settings import is_validation_enabled


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("=> Searching for schema files...")
        try:
            if is_validation_enabled():
                print("--> Schema validation enabled. Checking state..")
            load_all_event_schemas()
        except EventSchemaError as e:
            print("Missing or invalid event schemas:")
            print(e)
        else:
            print("--> Detected events:")
            for item in schemas.keys():
                print("--> {}".format(item))
            print("--> All schemas valid!")
        print("=> Done.")
