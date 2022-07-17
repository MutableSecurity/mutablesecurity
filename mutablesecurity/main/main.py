"""Module for orchestrating all the other modules."""
import inspect
import typing

from pyinfra import host

from mutablesecurity.helpers.exceptions import (
    FailedConnectionToHostsException,
    FailedExecutionException,
    MutableSecurityException,
)
from mutablesecurity.leader import Connection, Leader
from mutablesecurity.logger import Logger
from mutablesecurity.main.deployments import (
    ResponseTypes,
    SecurityDeploymentResult,
)
from mutablesecurity.solutions_manager import SolutionsManager

if typing.TYPE_CHECKING:
    from mutablesecurity.solutions.base import BaseSolution


class Main:
    """Class orchestrating all the other modules."""

    logger: Logger
    dev_mode: bool

    def __init__(self, verbose: bool = True, dev_mode: bool = False) -> None:
        """Initialize the object.

        Args:
            verbose (bool): Boolean indicating if the logging is verbose.
                Defaults to True.
            dev_mode (bool): Boolean indicating if running in developer mode
        """
        self.logger = Logger(verbose)
        self.dev_mode = dev_mode

    def run(
        self,
        connections: typing.List[Connection],
        solution_id: str,
        operation_name: str,
        additional_arguments: dict,
    ) -> typing.List[SecurityDeploymentResult]:
        """Run an operation of a solution against a set of connections.

        Args:
            connections (typing.List[Connection]): List of connections
            solution_id (str): Solution's name
            operation_name (str): Operation's name, implemented in the given
                solution
            additional_arguments (dict): Additional arguments to be passed to
                the operation

        Raises:
            FailedConnectionToHostsException: The hosts connection failed.
            FailedExecutionException: The execution failed.

        Returns:
            typing.List[SecurityDeploymentResult]: List of deployments' results
        """
        # Attach connection
        leader_module = Leader()
        for connection in connections:
            leader_module.attach_connection(connection)

        # Connect
        try:
            leader_module.connect()
        except FailedConnectionToHostsException as exception:
            raise exception

        # Execute
        solution_class = SolutionsManager().get_solution_by_id(solution_id)
        solution = solution_class()
        operation = SolutionsManager().get_operation_by_id(
            solution, operation_name
        )
        try:
            guarded_operation = exported_functionality(operation, solution)
            leader_module.run_operation(
                guarded_operation, **additional_arguments
            )
        except FailedExecutionException as exception:
            raise exception

        return leader_module.results


def exported_functionality(
    function: typing.Callable, solution: "BaseSolution"
) -> typing.Callable:
    """Decorate an exported solution method.

    It includes:
    - Catching and reraising MutableSecurityException exceptions
    - Passing required keyword arguments.

    Args:
        function (typing.Callable): Function to decorate
        solution (BaseSolution): Solution

    Returns:
        typing.Callable: Decorator
    """

    def inner(*args: tuple, **kwargs: typing.Any) -> None:
        """Execute the ones mentioned above.

        Args:
            args (tuple): Decorated function positional arguments
            kwargs (typing.Any): Decorated function keyword arguments
        """
        # Extract only the keyword parameters needed by the function
        signature = inspect.signature(function.__func__)  # type: ignore
        parameters = signature.parameters
        required_kwargs = {}
        if len(parameters) > 1:
            for key, _ in parameters.items():
                if key == "self" or key == "cls":
                    continue

                required_kwargs[key] = kwargs[key]

        try:
            raw_result = function.__func__(  # type: ignore
                solution, *args, **required_kwargs
            )

            # Store the result into the leader module
            result = SecurityDeploymentResult(
                str(host),
                ResponseTypes.SUCCESS,
                "The operation was successfully executed!",
                raw_result,
            )
            Leader().publish_result(result)
        except MutableSecurityException as exception:
            # Store the result into the leader module
            result = SecurityDeploymentResult(
                str(host), ResponseTypes.ERROR, str(exception)
            )
            Leader().publish_result(result)

    return inner