"""Module defining an abstract action."""
import inspect
import typing

from mutablesecurity.helpers.data_type import DataType, DataTypeFactory
from mutablesecurity.helpers.exceptions import (
    ActionArgumentNotPresentException,
    InvalidDataValueToConvertException,
    InvalidNumberOfActionArgumentsException,
    InvalidValueForActionArgumentException,
    SolutionActionNotFoundException,
    SolutionObjectNotFoundException,
)
from mutablesecurity.helpers.type_hints import PyinfraOperation
from mutablesecurity.solutions.base.object import BaseManager, BaseObject
from mutablesecurity.solutions.base.result import (
    BaseGenericObjectsDescriptions,
    KeysDescriptions,
)


class BaseAction(BaseObject):
    """Abstract class modeling a possible action performed by the solution.

    This class is stateless.
    """

    ACT: PyinfraOperation
    PARAMETERS_DATA_TYPES: typing.Dict[str, typing.Type[DataType]]

    def __init_subclass__(
        cls: typing.Type["BaseAction"],
    ) -> None:
        """Initialize the child class after definition."""
        super().__init_subclass__()

        cls.PARAMETERS_DATA_TYPES = {}
        for key, value in inspect.signature(cls.ACT).parameters.items():
            cls.PARAMETERS_DATA_TYPES[
                key
            ] = DataTypeFactory.create_from_annotation(value.annotation)

    @classmethod
    @property
    def PARAMETERS_KEYS(  # noqa: N802 # pylint: disable=invalid-name
        cls: typing.Type["BaseAction"],
    ) -> str:
        """Get the keys of the required parameters.

        Returns:
            str: Parameters keys
        """
        params_str = [
            f"{key} ({value.ALIAS})"
            for key, value in cls.PARAMETERS_DATA_TYPES.items()
        ]

        return ", ".join(params_str)

    @classmethod
    def execute(cls: typing.Type["BaseAction"]) -> None:
        """Execute the action."""
        cls.ACT()


class ActionsManager(BaseManager):
    """Class managing the actions of a solution."""

    objects_descriptions: BaseGenericObjectsDescriptions
    KEYS_DESCRIPTIONS: KeysDescriptions = {
        "identifier": "Identifier",
        "description": "Description",
        "parameters_keys": "Expected Parameters Keys and Types",
    }

    def __init__(self, actions: typing.Sequence[BaseAction]) -> None:
        """Initialize the instance.

        Args:
            actions (typing.Sequence[BaseAction]): List of actions to be added
        """
        super().__init__(actions)

        self.objects_descriptions = [
            {
                "identifier": action.IDENTIFIER,
                "description": action.DESCRIPTION,
                "parameters_keys": action.PARAMETERS_KEYS,
            }
            for action in actions
        ]

    def __parse_arguments(
        self, action: BaseAction, args: dict
    ) -> typing.Dict[str, typing.Any]:
        signature = inspect.signature(action.ACT)
        params = signature.parameters

        # Check if only the mandatory keys are present
        expected_keys = params.keys()
        if len(expected_keys) != len(args):
            raise InvalidNumberOfActionArgumentsException()
        for key in expected_keys:
            if key not in args:
                raise ActionArgumentNotPresentException()

        # Convert the arguments to their real types
        for key in params.keys():
            real_type = action.PARAMETERS_DATA_TYPES[key]

            try:
                args[key] = real_type.convert_string(args[key])
            except InvalidDataValueToConvertException as exception:
                raise InvalidValueForActionArgumentException() from exception

        return args

    def execute(self, identifier: str, args: dict) -> None:
        """Execute a specific action, with the given arguments.

        Args:
            identifier (str): Action identifier
            args (dict): Action's arguments

        Raises:
            SolutionActionNotFoundException: The identifier does not correspond
                to any action.
        """
        try:
            action: BaseAction = self.get_object_by_identifier(
                identifier
            )  # type: ignore[assignment]
        except SolutionObjectNotFoundException as exception:
            raise SolutionActionNotFoundException() from exception

        parsed_args = self.__parse_arguments(action, args)

        action.ACT(**parsed_args)
