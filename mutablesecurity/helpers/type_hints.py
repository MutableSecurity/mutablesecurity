"""Module for defining reusable custom type hints."""

import typing

# Function decorator
Decorator = typing.Callable[..., typing.Callable[..., None]]

# Tuple of connection string - additional details or only connection string
# identifying a host
PyinfraHostTuple = typing.Union[typing.Tuple[str, dict], str]

# Dump of a pyinfra connection
PyinfraConnectionDump = typing.Union[str, typing.Tuple[str, dict]]

# pyinfra operation
PyinfraOperation = typing.Annotated[typing.Callable, "pyinfra Operation"]

# Matrix of strings
StringMatrix = typing.List[typing.List[str]]
