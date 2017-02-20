from ..shortcuts import get_entity_or_404, get_aggregate_or_404
from django.http import Http404

import pytest


def test_get_entity_or_404_item_exists():
    """
    ES store provides a dictionary style item verification.
    """
    repo = {'id': 'entity'}
    assert get_entity_or_404(repo, 'id') == 'entity'


def test_get_entity_or_404_item_does_not_exists():
    repo = {}
    with pytest.raises(Http404) as exc_info:
        get_entity_or_404(repo, 'id')


def test_get_aggregate_or_404_item_exists():
    repo = {'id': 'aggregate'}
    assert get_aggregate_or_404(repo, 'id') == 'aggregate'


def test_get_aggregate_or_404_item_does_not_exists():
    repo = {}
    with pytest.raises(Http404) as exc_info:
        get_aggregate_or_404(repo, 'id')
