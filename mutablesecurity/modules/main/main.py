import logging
from inspect import signature

from pyinfra.api.deploy import add_deploy
from pyinfra.api.exceptions import PyinfraError
from pyinfra.api.operations import run_ops

from ..leader import Leader
from ..solutions_manager import AbstractSolution, AvailableSolution, SolutionsManager


class Main:
    logger = logging.getLogger("mutablesecurity")

    @staticmethod
    def get_available_solutions():
        solutions = [element.name for element in AvailableSolution]

        return solutions

    @staticmethod
    def get_available_operations():
        members = dir(AbstractSolution)
        methods = [
            member.upper()
            for member in members
            if member[0] != "_" and callable(getattr(AbstractSolution, member))
        ]

        return methods

    @staticmethod
    def run(connection_details, solution_name, operation_name, additional_arguments):
        try:
            # Connect to local or remote depending on the set host
            if connection_details[0]:
                host, ssh_port, ssh_user, ssh_password = connection_details
                state = Leader.connect_to_ssh_with_password(
                    host, ssh_port, ssh_user, ssh_password
                )
            else:
                local_password = connection_details[3]
                state = Leader.connect_to_local(local_password)
        except:
            return {
                "success": False,
                "message": "The host is down or the credentials are invalid.",
                "raw_result": None,
            }

        # Get the module's method dealing with the provided operation
        solution_class = SolutionsManager.get_solution_by_name(solution_name)
        operation_method = getattr(solution_class, operation_name.lower())
        meta = getattr(solution_class, "meta")

        # Run the required deployment
        try:
            # Check the number of the arguments. Two of them are inherited from
            # the pyinfra deployment.
            if len(signature(operation_method).parameters) == 2:
                add_deploy(state, operation_method)
            else:
                add_deploy(state, operation_method, **additional_arguments)

            # Run the operations
            run_ops(state)
            result = getattr(solution_class, "result")

            # Check the result
            if not result:
                is_fail = True
            else:
                is_fail = False
        except PyinfraError:
            result = None
            is_fail = True

        # Check the result and build the response
        message = meta["messages"][operation_name][int(is_fail)]
        response = {"success": not is_fail, "message": message, "raw_result": result}

        return response
