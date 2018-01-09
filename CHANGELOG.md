0.14.0
======

- Added index on the `stored_entity_id` field which fixes performance
  issue when there are many events. It requires migration, version
  change reflects that.


0.13.4
======

- Switched to `schema_version = None` default when deserializing
  events without `schema_version`.


0.13.3
======

- Stopped overriding `schema_version` if it exists.
- Started passing all event attributes to event constructor during
  deserialization. This allows to handle event structure migration
  ("upcasting") in each event's constructor: one can modify `kwargs`
  before calling `super().__init__`.


0.13.2
======

- Made `@abstract` non inheritable: now only classes explicitly marked
  with the `@abstract` decorator are abstract. Their subclasses are not.
  This was always the intended behavior.


0.13.1
======

- Switched to adding `schema_version` to event objects themselves
  instead of just transcoded events. This way events will pass
  validation if their Avro schemas require `schema_version`.

- Renamed setting responsible for the above feature
  from `EVENT_TRANSCODER.ADDS_EVENT_VERSION_TO_DATA`
  to `ADDS_SCHEMA_VERSION_TO_EVENT_DATA`.


0.13.0
======

- Renamed `Event.schema_version` to `Event.version`.
- Started setting `Event.version` based on schema file with the highest number.
- Added event version to stored event envelope under the `event_version` key.
- Added setting to add event version to event data as well (see "Event version" section in README).


0.12.0
======

- Started automatically choosing Avro schemas with the highest version
  (based on file names on disk).

- Changed way how event type string is computed. For example,
  given User aggregate and Created event, now it would be "user_created"
  (while in older versions that would be simply "Created" which sometimes
  is not sufficient enough). Moreover it is now possible to override that
  with `event_type` attribute set on an event class.

0.9.4
=====
- Made `DomainEvent.metadata` optional during serialization ([PR #10](https://github.com/ApplauseOSS/djangoevents/pull/10)).

0.9.3
=====
- Fixed exception when DomainEvent.metadata is not defined on saving to event store. [PR#7](https://github.com/ApplauseOSS/djangoevents/pull/7)

0.9.2
=====

- When attempt to create an aggregate using ID of existing one,
  `esdjango.exceptions.AlreadyExists` error would be raised.
  NOTE: This is possibly a breaking change: previously Django's
  standard IntegrityError was raised.
