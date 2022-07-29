"""Module defining a common interface for all the other objects."""

import typing
from abc import ABC

from mutablesecurity.helpers.exceptions import SolutionObjectNotFoundException
from mutablesecurity.solutions.base.result import (
    BaseGenericObjectsDescriptions,
    KeysDescriptions,
)


class BaseObject(ABC):
    """Common interface for identifiable objects, with descriptions."""

    IDENTIFIER: str
    DESCRIPTION: str


class BaseManager:
    """Class managing objects."""

    KEYS_DESCRIPTIONS: KeysDescriptions = {
        "identifier": "Identifier",
        "description": "Description",
    }
    objects: typing.Dict[str, BaseObject]
    objects_descriptions: BaseGenericObjectsDescriptions

    def __init__(self, objects: typing.Sequence[BaseObject]) -> None:
        """Initialize the instance.

        Args:
            objects (typing.Sequence[BaseObject]): List of objects to be added
        """
        self.objects = {
            current_object.IDENTIFIER: current_object
            for current_object in objects
        }
        self.objects_descriptions = [
            {
                "identifier": current_object.IDENTIFIER,
                "description": current_object.DESCRIPTION,
            }
            for current_object in objects
        ]

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
