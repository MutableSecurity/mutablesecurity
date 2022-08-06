"""Package for stringifying the objects showed in a user interface."""
import typing


def to_str(obj: typing.Any) -> str:
    """Stringify an object.

    Args:
        obj (typing.Any): Object

    Returns:
        str: String representation
    """
    if obj is None:
        return ""
    elif isinstance(obj, type):
        if not (name := getattr(obj, "ALIAS", None)):
            name = obj.__name__

        return name
    elif isinstance(obj, list):
        return ", ".join([to_str(elem) for elem in obj])

    return str(obj)
