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
