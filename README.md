# Welcome to djangoevents' documentation!
djangoevents offers building blocks for building Event Sourcing Django applications.

[![Build Status](https://travis-ci.org/ApplauseOSS/djangoevents.svg?branch=master)](https://travis-ci.org/ApplauseOSS/djangoevents)
[![Build Status](https://travis-ci.org/ApplauseOSS/djangoevents.svg?branch=devel)](https://travis-ci.org/ApplauseOSS/djangoevents)

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

### BaseAggregate
It is required to place all aggregate definitions in `aggregates.py` module of a Django application.

BaseEntity is a wrapper over EventSourcedEntity from eventsourcing's EventSourcedEntity. It is used to define Aggregates, its domain events and how domain events apply changes to Aggregates in one place.

```python
from djangoevents import BaseAggregate

class Todo(BaseAggregate):

    class Created(BaseAggregate.Created):
        def mutate_event(self, event, cls):
            return cls(
                entity_id=event.entity_id,
                entity_version=event.entity_version,
                domain_event_id=event.domain_event_id,
                label=event.label,
                done=False,
            )

    class ChangedLabel(BaseAggregate.AttributeChanged):
        def mutate_event(self, event, instance):
            instance.label = event.label
            return instance
```


### EventSourcingWithDjango
For seamless integration with Django, we created an implementation of eventsourcing's eventStore using Django ORM and built EventSourcingWithDjango on top of it. By using EventSourcingWithDjango, the Django ORM will be used to store events. Here is a short example of how to create and save an event:
```python
from djangoevents import EventSourcingWithDjango
from djangoevents import store_event

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
store_event(todo_created_event)

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
We have ported commonly used functionality from [eventsourcing](https://github.com/johnbywater/eventsourcing) to the top level of this library. Please import from `djangoevents` because we might have extended functionality of some classes and functions.

```python
from djangoevents import DomainEvent                    # from eventsourcing.domain.model.entity import DomainEvent
from djangoevents import EventSourcedEntity             # from eventsourcing.domain.model.entity import EventSourcedEntity
from djangoevents import entity_mutator                 # from eventsourcing.domain.model.entity import entity_mutator
from djangoevents import singledispatch                 # from eventsourcing.domain.model.entity import singledispatch

from djangoevents import store_event                    # from eventsourcing.domain.model.events import publish
from djangoevents import subscribe                      # from eventsourcing.domain.model.events import subscribe
from djangoevents import unsubscribe                    # from eventsourcing.domain.model.events import unsubscribe

from djangoevents import subscribe_to                   # from eventsourcing.domain.model.decorators import subscribe_to

from djangoevents import EventSourcedRepository         # from eventsourcing.infrastructure.event_sourced_repo import EventSourcedRepository
```

### Documenting event schema

Event schema validation is disabled by default. To enable it for the whole project please add `DJANGOEVENTS_CONFIG` to project's `settings.py`:

```python
DJANGOEVENTS_CONFIG = {
    ...
    'EVENT_SCHEMA_VALIDATION': {
        'ENABLED': True,
        'SCHEMA_DIR': 'avro',
    },
    ...
}
```

Once this is enabled avro schema definition will be required for all events in the system.
The only exception to this rule are events of abstract aggregates:

```python
from djangoevents import BaseAggregate, abstract

@abstract
class Animal(BaseAggregate):
    class Created(BaseAggregate.Created):
        def mutate_event(self, event, cls):
            return cls(
                entity_id=event.entity_id,
                entity_version=event.entity_version,
                domain_event_id=event.domain_event_id,
                label=event.label,
                done=False,
            )

class Dog(Animal):
    pass

```

In the example above `Animal` was defined as an `abstract` aggregate. Its goal is to keep all common implementation in a single place
for child classes. No event specification is required for `Animal.Created` abstract aggregates. It needs to be present for `Dog.Created` though.

**It is expected that each service will fully document all events emitted through avro schema definitions**. Read more about [avro format specification](https://avro.apache.org/docs/1.7.7/spec.html).

By default djangoevents assumes event schemas will be placed in `avro` folder located at project's root directory as specifed below:

```bash
$ tree project
|- src
|--- manage.py
|--- ..
|-avro
|--- aggragate_name/
|----- v1_aggregate_name_test_event1.json
|----- v1_aggregate_name_test_event2.json
...
```

```bash
$ cat avro/aggragate_name/v1_aggregate_name_test_event1.json

{
  "name": "aggregate_name_test_event1",
  "type": "record",
  "doc": "Sample Event",
  "fields": [
    {
      "name": "entity_id",
      "type": "string",
      "doc": "ID of a the asset."
    },
    {
      "name": "entity_version",
      "type": "long",
      "doc": "Aggregate revision"
    },
    {
      "name": "domain_event_id",
      "type": "string",
      "doc": "ID of the last modifying event"
    },
  ]
}

```

Once event schema validation is enabled for your services, following changes will apply:
  * At startup (`djangoevents.AppConfig.ready()`) schemas of events of all non-abstract aggregates will be loaded, validated & cached. If any error occurs warning message will be printed in the console.
  * `store_event()` will validate your event before storing it to the event journal.

In cases where enabling validation for the whole project is not possible you can enforce schema validation on-demand by adding `force_valdate=True` parameter to `store_event()` call.


### Event version

`djangoevents` detects the latest version of your event based on Avro schema files it finds. Version is stored as the `.version` property of an event *class*, e.g. `SomeEvent.version`. Version is added to stored event envelope under the `event_version` key.

For compatibility with some systems, we provide an option to add event version to event data as well (essentially `stored_event.event_data['schema_version'] = stored_event.event_version`). This functionality is disabled by default, but you can enable it in your project's settings:

```python
DJANGOEVENTS_CONFIG = {
    ...
    'ADDS_SCHEMA_VERSION_TO_EVENT_DATA': True,
    ...
}
```


## Development
#### Build
    $ make install
#### Run tests
    $ source venv/bin/activate
    $ pytest
