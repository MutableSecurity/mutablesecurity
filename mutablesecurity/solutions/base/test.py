"""Module defining an abstract log source."""
import typing
from enum import Enum

from pyinfra import host
from pyinfra.api import FactBase
from pyinfra.operations import python

from mutablesecurity.helpers.exceptions import (
    FailedSolutionTestException,
    MutableSecurityException,
    SolutionObjectNotFoundException,
    SolutionTestNotFoundException,
)
from mutablesecurity.helpers.type_hints import PyinfraOperation
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

    # Used to determine if the solution integrates with other components of the
    # infrastructure
    INTEGRATION = 4


class BaseTest(BaseObject):
    """Abstract class modeling an atomic step for testing the solution.

    The tests does not includes a success code because they are ephemeral. The
    old response, once returned, can be discarded. So this class is stateless.
    """

    TEST_TYPE: TestType
    FACT: FactBase
    FACT_ARGS: tuple
    TRIGGER: PyinfraOperation


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
        only_check: bool = False,
        expected_value: bool = True,
        exception_when_fail: typing.Type[
            MutableSecurityException
        ] = FailedSolutionTestException,
    ) -> BaseConcreteResultObjects:
        """Make a test or all the testsuite.

        Args:
            identifier (str): Test identifier. Defaults to None if all the
                testsuite is executed.
            filter_type (TestType): Test type used as a filter. Defaults to
                None.
            only_check (bool): Boolean indicating if the tests raises an
                exception if they not pass
            expected_value (bool): Value to be returned by the facts. Defaults
                to True.
            exception_when_fail (typing.Type[MutableSecurityException]):
                Exception type to instantiate and raise when a test fails (only
                when only_check is False). Defaults to
                FailedSolutionTestException.

        Raises:
            SolutionTestNotFoundException: Invalid test identifier

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
        result: typing.Dict[str, bool] = {}
        for test in tests_list:
            try:
                test.TRIGGER()
            except AttributeError:
                pass

        def error(*_: tuple) -> None:
            nonlocal exception_when_fail
            nonlocal only_check

            if not only_check:
                raise exception_when_fail()

        for test in tests_list:

            def stage(
                *,
                fact_to_get: FactBase,
                args: tuple,
                test_identifier: str,
                expected_value: bool,
                tests_results: typing.Dict[str, bool],
                only_check: bool
            ) -> None:
                """Trick pyinfra to get the fact after the trigger operation.

                Args:
                    fact_to_get (FactBase): Fact to get
                    args (tuple): Fact arguments
                    test_identifier (str): Identifier of the test to be
                        executed
                    expected_value (bool): Value to be expected
                    tests_results (typing.Dict[str, bool]): Dictionary with
                        test results
                    only_check (bool): Boolean indicating if an exception is
                        raised when a test fails

                Raises:
                    Exception: Generic exception raised in the Greenlet thread
                        to highlight an error occurrence
                """
                result = host.get_fact(fact_to_get, *args)

                if result != expected_value and not only_check:
                    raise Exception()

                tests_results[test_identifier] = result

            args = getattr(test, "FACT_ARGS", ())
            python.call(
                function=stage,
                fact_to_get=test.FACT,
                args=args,
                ignore_errors=True,
                test_identifier=test.IDENTIFIER,
                expected_value=expected_value,
                tests_results=result,
                on_error=error,
                only_check=only_check,
            )

        return result
