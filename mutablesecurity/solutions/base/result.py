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

    - Is concrete a long output?

        No
    """

    keys_descriptions: KeysDescriptions
    generic_objects_descriptions: BaseGenericObjectsDescriptions
    concrete_objects: BaseConcreteResultObjects

    def __init__(
        self,
        keys_descriptions: KeysDescriptions,
        generic_objects_descriptions: BaseGenericObjectsDescriptions,
        concrete_objects: BaseConcreteResultObjects,
        is_long_output: bool,
    ) -> None:
        """Initialize an instance.

        Args:
            keys_descriptions (KeysDescriptions): Descriptions of keys
                specific to an object
            generic_objects_descriptions (BaseGenericObjectsDescriptions):
                Static descriptions of object
            concrete_objects (BaseConcreteResultObjects): Concrete, dynamic
                values of the objects
            is_long_output (bool): Boolean indicating if the concrete objects
                can contain long output and should be processed accordingly
        """
        self.keys_descriptions = keys_descriptions
        self.generic_objects_descriptions = generic_objects_descriptions
        self.concrete_objects = concrete_objects
        self.is_long_output = is_long_output
