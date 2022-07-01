"""Module for orchestrating all the other modules."""
import typing

from src.helpers.exceptions import (
    FailedConnectionToHostsException,
    FailedExecutionException,
)
from src.leader import Connection, Leader
from src.logger import Logger
from src.main.deployments import ResponseTypes, SecurityDeploymentResult
from src.solutions_manager import SolutionsManager


class Main:
    """Class orchestrating all the other modules."""

    logger: Logger

    def __init__(self, verbose: bool = True) -> None:
        """Initialize the object.

        Args:
            verbose (bool): Boolean indicating if the logging is verbose.
                Defaults to True.
        """
        self.logger = Logger(verbose)

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
        solution = SolutionsManager().get_solution_by_id(solution_id)
        operation = SolutionsManager().get_operation_by_id(
            solution, operation_name
        )
        try:
            leader_module.run_operation(operation, **additional_arguments)
        except FailedExecutionException as exception:
            raise exception

        # TODO: After finishing the SolutionManager module, get its result or
        #       error message.
        return [
            SecurityDeploymentResult(
                "local", ResponseTypes.SUCCESS, "Success", None
            )
        ]
