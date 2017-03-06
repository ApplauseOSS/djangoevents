class DjangoeventsError(Exception):
    pass


class AlreadyExists(DjangoeventsError):
    pass


class EventSchemaError(DjangoeventsError):
    pass
