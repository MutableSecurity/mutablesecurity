"""Module for orchestrating all the other modules."""
import typing

from ..helpers.exceptions import (
    FailedConnectionToHostsException,
    FailedExecutionException,
)
from ..leader import Connection, Leader
from ..logger.logger import _setup_logging
from ..solutions_manager import SolutionsManager
from .deployments import ResponseTypes, SecurityDeploymentResult


class Main:
    """Class orchestrating all the other modules."""

    def __init__(self, verbose: typing.Optional[bool] = True) -> None:
        """Initialize the object.

        Args:
            verbose (bool, optional): Boolean indicating if the logging is
                verbose. Defaults to True.
        """
        _setup_logging(verbose)

    def run(
        self,
        connections: typing.List[Connection],
        solution_name: str,
        operation_name: str,
        additional_arguments: dict,
    ) -> typing.List[SecurityDeploymentResult]:
        """Run an operation of a solution against a set of connections.

        Args:
            connections (typing.List[Connection]): List of connections
            solution_name (str): Solution's name
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
        solution = SolutionsManager().get_solution_by_name(solution_name)
        operation = getattr(solution, operation_name.lower())
        try:
            leader_module.run_operation(operation, **additional_arguments)
        except FailedExecutionException as exception:
            raise exception

        # TODO: After finishing the SolutionManager module, get its result or
        #       error message
        return [
            SecurityDeploymentResult(
                "local", ResponseTypes.SUCCESS, "Success", None
            )
        ]
