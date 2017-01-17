from django.http import Http404


def get_entity_or_404(repo, entity_id):
    """
    Uses `repo` to return most recent state of the entity. Raises a Http404 exception if the
    `entity_id` does not exist.

    `repo` has to be a EventSourcedRepository object.
    """
    if entity_id not in repo:
        raise Http404
    return repo[entity_id]
