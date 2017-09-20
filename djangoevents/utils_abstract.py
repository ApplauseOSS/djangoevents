_abstract_classes = set()


def abstract(cls):
    """
    Decorator marking classes as abstract.

    The "abstract" mark is an internal tag.  Classes can be checked for
    being abstract with the `is_abstract` function.  The tag is non
    inheritable: every class or subclass has to be explicitly marked
    with the decorator to be considered abstract.
    """

    _abstract_classes.add(cls)
    return cls


def is_abstract(cls):
    return cls in _abstract_classes
