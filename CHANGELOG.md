dev
===

- Started automatically choosing Avro schemas with the highest version (based on file names on disk).


0.12
====

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
