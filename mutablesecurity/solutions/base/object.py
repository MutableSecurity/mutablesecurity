"""Module defining a common interface for all the other objects."""

import typing
from abc import ABC

from mutablesecurity.helpers.exceptions import SolutionObjectNotFoundException


class BaseObject(ABC):
    """Common interface for identifiable objects, with descriptions."""

    IDENTIFIER: str
    DESCRIPTION: str


class BaseManager:
    """Class managing objects."""

    objects: typing.Dict[str, BaseObject]

    def __init__(self, objects: typing.Sequence[BaseObject]) -> None:
        """Initialize the instance.

        Args:
            objects (typing.Sequence[BaseObject]): List of objects to be added
        """
        self.objects = {
            current_object.IDENTIFIER: current_object
            for current_object in objects
        }

    def represent_as_matrix(self) -> typing.List[typing.List[str]]:
        """Represent the objects as a matrix.

        Returns:
            typing.List[typing.List[str]]: Matrix with objects' details
        """
        result = [["Identifier", "Description"]]

        for key, current_object in self.objects.items():
            result.append([key, current_object.DESCRIPTION])

        return result

    def get_object_by_identifier(self, identifier: str) -> BaseObject:
        """Search an object by its identifier.

        Args:
            identifier (str): Identifier

        Raises:
            SolutionObjectNotFoundException: Object not found

        Returns:
            BaseObject: Found object
        """
        try:
            return self.objects[identifier]
        except KeyError as exception:
            raise SolutionObjectNotFoundException() from exception
