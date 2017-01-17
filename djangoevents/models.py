from django.db import models


class Event(models.Model):
    event_id = models.CharField(max_length=255, db_index=True)
    event_type = models.CharField(max_length=255)
    event_data = models.TextField()
    aggregate_id = models.CharField(max_length=255, db_index=True)
    aggregate_type = models.CharField(max_length=255)
    aggregate_version = models.IntegerField()
    create_date = models.DateTimeField()
    metadata = models.TextField()
    module_name = models.CharField(max_length=255, db_column='_module_name')
    class_name = models.CharField(max_length=255, db_column='_class_name')
    stored_entity_id = models.CharField(max_length=255, db_column='_stored_entity_id')

    class Meta:
        unique_together = (("aggregate_id", "aggregate_type", "aggregate_version"),)
        db_table = 'event_journal'

    def __str__(self):
        return '%s.%s | %s | %s' % (self.aggregate_type, self.event_type, self.event_id, self.create_date)
