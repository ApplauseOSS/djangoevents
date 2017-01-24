# Welcome to djangoevents' documentation!
djangoevents offers building blocks for building Event Sourcing Django applications.

## Setup
Install with pip:

```
pip install djangoevents
```

Include in settings.py:
```python
INSTALLED_APPS = [
    ...
    'djangoevents',
    ...
]
```

## Event Sourcing Components
djangoevents takes advantage of [eventsourcing](https://github.com/johnbywater/eventsourcing) library for handling event sourcing and replaces its storage backend with Django Model for seamless integration with Django.

### BaseEntity
BaseEntity is a wrapper over EventSourcedEntity from eventsourcing's EventSourcedEntity. It is used to define Aggregates, its domain events and how domain events apply changes to Aggregates in one place.
```python
from djangoevents import BaseEntity

class Todo(BaseEntity):

    class Created(BaseEntity.Created):
        def mutate_event(self, event, cls):
            return cls(
                entity_id=event.entity_id,
                entity_version=event.entity_version,
                domain_event_id=event.domain_event_id,
                label=event.label,
                done=False,
            )

    class ChangedLabel(BaseEntity.AttributeChanged):
        def mutate_event(self, event, instance):
            instance.label = event.label
            return instance
```

### EventSourcingWithDjango
For seamless integration with Django, we created an implementation of eventsourcing's eventStore using Django ORM and built EventSourcingWithDjango on top of it. By using EventSourcingWithDjango, the Django ORM will be used to store events. Here is a short example of how to create and save an event:
```python
from djangoevents import EventSourcingWithDjango
from djangoevents import publish

class Todo(EventSourcedEntity):
    ...

class TodoRepository(EventSourcedRepository):
    domain_class = Todo

es_app = EventSourcingWithDjango()
repo = es_app.get_repo_for_entity(Todo)

# publish event (saves in the database)
todo_created_event = Todo.Created(
    entity_id='6deaca4c-d866-4b28-9878-8814a55a4688',
    label='my next thing to do',
    metadata={'command_id': '...'}
)
publish(todo_created_event)

# get todo aggregate from repo by aggregate id
my_todo = repo['6deaca4c-d866-4b28-9878-8814a55a4688']

```


### Event handlers

If extra event handling on event publish other than saving it to event journal is a requirement, add `handlers.py` file in your app and use _subscribe_to_ decorator with the DomainEvent class you intent to listen on. Example:


```python
from djangoevents import subscribe_to
from myapp.entities import Miracle

@subscribe_to(Miracle.Happened)
def miracle_handler(event):
    print(" => miracle happened! update your projections here!")
```


Note: name of that file is important. There is auto-import mechanism that would import
`handlers.py` file for all apps mentioned in `INSTALLED_APPS`. You can put handler
functions anywhere you like but you'd need to make sure it's imported somehow.

### Import shortcuts
For the ease of use, we have ported commonly used functionality from [eventsourcing](https://github.com/johnbywater/eventsourcing) to the top level of this library.

```python
from djangoevents import DomainEvent                    # from eventsourcing.domain.model.entity import DomainEvent
from djangoevents import EventSourcedEntity             # from eventsourcing.domain.model.entity import EventSourcedEntity
from djangoevents import entity_mutator                 # from eventsourcing.domain.model.entity import entity_mutator
from djangoevents import singledispatch                 # from eventsourcing.domain.model.entity import singledispatch

from djangoevents import publish                        # from eventsourcing.domain.model.events import publish
from djangoevents import subscribe                      # from eventsourcing.domain.model.events import subscribe
from djangoevents import unsubscribe                    # from eventsourcing.domain.model.events import unsubscribe

from djangoevents import subscribe_to                   # from eventsourcing.domain.model.decorators import subscribe_to

from djangoevents import EventSourcedRepository         # from eventsourcing.infrastructure.event_sourced_repo import EventSourcedRepository
```

## Development
#### Build
    $ make install
#### Run tests
    $ source venv/bin/activate
    $ pytest
