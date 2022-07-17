"""Module defining an abstract log source."""
import typing
from enum import Enum

from pyinfra import host
from pyinfra.api import FactBase

from mutablesecurity.helpers.exceptions import (
    FailedSolutionTestException,
    SolutionObjectNotFoundException,
    SolutionTestNotFoundException,
)
from mutablesecurity.solutions.base.object import BaseManager, BaseObject
from mutablesecurity.solutions.base.result import (
    BaseConcreteResultObjects,
    BaseGenericObjectsDescriptions,
    KeysDescriptions,
)


class TestType(Enum):
    """Enumeration for types of tests."""

    # Used to determine if the system is compatible
    REQUIREMENT = 0

    # Used to determine if the solution is installed on the machine
    PRESENCE = 1

    # Used to determine if the solution is running (with or without achieving
    # security)
    OPERATIONAL = 2

    # Used to determine if the solution achieves its security-related goals
    SECURITY = 3

    # Used to test if the solution integrates with other components of the
    # infrastructure
    INTEGRATION = 4


class BaseTest(BaseObject):
    """Abstract class modeling an atomic step for testing the solution.

    The tests does not includes a success code because they are ephemeral. The
    old response, once returned, can be discarded. So this class is stateless.
    """

    TEST_TYPE: TestType
    FACT: FactBase


class TestsManager(BaseManager):
    """Class managing the tests of a solution."""

    objects_descriptions: BaseGenericObjectsDescriptions
    KEYS_DESCRIPTIONS: KeysDescriptions = {
        "identifier": "Identifier",
        "description": "Description",
        "type": "Type",
    }

    def __init__(self, tests: typing.Sequence[BaseTest]) -> None:
        """Initialize the instance.

        Args:
            tests (typing.Sequence[BaseTest]): List of tests to be added
        """
        super().__init__(tests)

        self.objects_descriptions = [
            {
                "identifier": test.IDENTIFIER,
                "description": test.DESCRIPTION,
                "type": test.TEST_TYPE.name,
            }
            for test in tests
        ]

    def test(
        self,
        identifier: typing.Optional[str] = None,
        filter_type: typing.Optional[TestType] = None,
        only_check: typing.Optional[bool] = False,
    ) -> BaseConcreteResultObjects:
        """Make a test or all the testsuite.

        Args:
            identifier (str, optional): Test identifier.
                Defaults to None if all the testsuite is executed.
            filter_type (TestType, optional): Test type used as a filter
            only_check (bool, optional): Boolean indicating if the tests raises
                an exception if they not pass

        Raises:
            SolutionTestNotFoundException: Invalid test identifier
            FailedSolutionTestException: A test failed.

        Returns:
            BaseConcreteResultObjects: Result with the tests success indicators
        """
        # Get only the tests of interest
        tests_list = []
        if identifier:
            try:
                selected_test: BaseTest = self.get_object_by_identifier(
                    identifier
                )  # type: ignore[assignment]
            except SolutionObjectNotFoundException as exception:
                raise SolutionTestNotFoundException() from exception

            tests_list = [selected_test]
        elif filter_type:
            for raw_test in self.objects.values():
                test: BaseTest = raw_test  # type: ignore[assignment]

                if test.TEST_TYPE == filter_type:
                    tests_list.append(test)
        else:
            tests_list = list(self.objects.values())  # type: ignore[arg-type]

        # Execute the tests
        result = {}
        for test in tests_list:
            check = host.get_fact(test.FACT)
            if only_check:
                result[test.IDENTIFIER] = check
            elif not check:
                raise FailedSolutionTestException()

        return result
