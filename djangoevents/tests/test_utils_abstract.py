from djangoevents.domain import BaseAggregate
from djangoevents.domain import DomainEvent
from djangoevents.utils_abstract import abstract
from djangoevents.utils_abstract import is_abstract


def test_subclass_of_abstract_event_is_not_abstract():

    class Aggregate(BaseAggregate):

        @abstract
        class Event1(DomainEvent):
            pass

        class Event2(Event1):
            pass

    assert is_abstract(Aggregate.Event1)
    assert not is_abstract(Aggregate.Event2)
