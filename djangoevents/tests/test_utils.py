from djangoevents.domain import BaseAggregate
from djangoevents.domain import DomainEvent
from djangoevents.utils_abstract import abstract
from ..utils import camel_case_to_snake_case
from ..utils import list_aggregate_events
from ..utils import list_concrete_aggregates
from ..utils import _list_subclasses
from ..utils import _list_internal_classes
from unittest import mock
import pytest


def test_list_subclasses():
    class Parent:
        pass

    class Child(Parent):
        pass

    class GrandChild(Child):
        pass

    assert set(_list_subclasses(Parent)) == {Child, GrandChild}


def test_list_subclasses_when_none():
    class Parent:
        pass

    assert _list_subclasses(Parent) == []


def list_internal_classes():
    class Parent:
        class Child1:
            pass

        class Child2:
            class GrandChild:
                pass

    # Please note that GrandChild is not on the list!
    assert set(_list_internal_classes(Parent)) == {Parent.Child1, Parent.Child2}


def list_internal_classes_none():
    class Parent:
        pass

    assert _list_internal_classes(Parent) == []


def test_list_aggregates_skip_abstract():
    class Aggregate1(BaseAggregate):
        pass

    @abstract
    class Aggregate2(BaseAggregate):
        pass

    with mock.patch('djangoevents.utils._list_subclasses') as list_subclasses:
        list_subclasses.return_value = [Aggregate1, Aggregate2]
        aggregates = list_concrete_aggregates()
        assert aggregates == [Aggregate1]


def test_list_aggregates_none_present():
    with mock.patch('djangoevents.utils._list_subclasses') as list_subclasses:
        list_subclasses.return_value = []
        aggregates = list_concrete_aggregates()
        assert aggregates == []


def test_list_events_sample_event_appart_from_abstract():
    class Aggregate(BaseAggregate):
        class Evt1(DomainEvent):
            def mutate_event(self, *args, **kwargs):
                pass

        class Evt2(DomainEvent):
            def mutate_event(self, *args, **kwargs):
                pass

        class Evt3(DomainEvent):
            # No mutate_event present
            pass

        @abstract
        class Evt4(DomainEvent):
            def mutate_event(self, *args, **kwargs):
                pass

    events = list_aggregate_events(Aggregate)
    assert set(events) == {Aggregate.Evt1, Aggregate.Evt2}


def test_list_events_not_an_aggregate():
    events = list_aggregate_events(list)
    assert events == []


@pytest.mark.parametrize('name, expected_output', [
    ('UserRegistered', 'user_registered'),
    ('UserRegisteredWithEmail', 'user_registered_with_email'),
    ('HttpResponse', 'http_response'),
    ('HTTPResponse', 'http_response'),
    ('already_snake', 'already_snake'),
])
def test_camel_case_to_snake_case(name, expected_output):
    assert expected_output == camel_case_to_snake_case(name)
