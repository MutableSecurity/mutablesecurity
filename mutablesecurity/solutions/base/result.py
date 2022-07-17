"""Module for storing a base operation result."""
import typing

KeysDescriptions = typing.Dict[str, str]
BaseGenericObjectsDescriptions = typing.List[typing.Dict[str, typing.Any]]
BaseConcreteResultObjects = typing.Dict[str, typing.Any]


class ConcreteObjectsResult:
    """Class for storing an operation result.

    An example of stored information will be:
    - Keys descriptions

        {
            "identifier": "Identifier",
            "description": "Description",
            "type": "Type"
        }

    - Generic object descriptions

        [
            {
                "identifier": "uid",
                "description": "User's ID",
                "type": "int"
            },
        ]

    - Concrete objects

        {
            "uid": 0
        }
    """

    keys_descriptions: KeysDescriptions
    generic_objects_descriptions: BaseGenericObjectsDescriptions
    concrete_objects: BaseConcreteResultObjects

    def __init__(
        self,
        keys_descriptions: KeysDescriptions,
        generic_objects_descriptions: BaseGenericObjectsDescriptions,
        concrete_objects: BaseConcreteResultObjects,
    ) -> None:
        """Initialize an instance.

        Args:
            keys_descriptions (KeysDescriptions): Descriptions of keys
                specific to an object
            generic_objects_descriptions (BaseGenericObjectsDescriptions):
                Static descriptions of object
            concrete_objects (BaseConcreteResultObjects): Concrete, dynamic
                values of the objects
        """
        self.keys_descriptions = keys_descriptions
        self.generic_objects_descriptions = generic_objects_descriptions
        self.concrete_objects = concrete_objects
