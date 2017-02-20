from django.http import Http404
import warnings


def get_aggregate_or_404(repo, aggregate_id):
    """
    Uses `repo` to return most recent state of the aggregate. Raises a Http404 exception if the
    `aggregate_id` does not exist.

    `repo` has to be a EventSourcedRepository object.
    """
    if aggregate_id not in repo:
        raise Http404
    return repo[aggregate_id]


def get_entity_or_404(repo, entity_id):
    warnings.warn("`get_entity_or_404` is depreciated. Please switch to: `get_aggregate_or_404`", DeprecationWarning)
    return get_aggregate_or_404(repo, entity_id)
