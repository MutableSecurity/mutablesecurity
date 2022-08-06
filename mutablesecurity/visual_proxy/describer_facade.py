"""Module implementing a facade for describing a solution."""

import typing

from mutablesecurity.solutions.base import BaseSolution
from mutablesecurity.solutions.base.result import (
    BaseConcreteResultObjects,
    BaseGenericObjectsDescriptions,
    KeysDescriptions,
)
from mutablesecurity.visual_proxy.stringifier import to_str

Matrix = typing.List[typing.List[str]]


class SolutionFacade:
    """Facade for exposing the processed properties of a module."""

    solution: BaseSolution

    def __init__(self, solution: BaseSolution) -> None:
        """Initialize the instance.

        Args:
            solution (BaseSolution): Solution to work with
        """
        self.solution = solution


class ObjectsDescriberFacade(SolutionFacade):
    """Facade for exposing the collections of objects from a module."""

    def describe_information(self) -> Matrix:
        """Describe the information within a solution.

        Returns:
            Matrix: Matrix containing information details
        """
        return describe_solution_objects(
            self.solution.INFORMATION_MANAGER.KEYS_DESCRIPTIONS,
            self.solution.INFORMATION_MANAGER.objects_descriptions,
        )

    def describe_tests(self) -> Matrix:
        """Describe the tests within a solution.

        Returns:
            Matrix: Matrix containing tests details
        """
        return describe_solution_objects(
            self.solution.TESTS_MANAGER.KEYS_DESCRIPTIONS,
            self.solution.TESTS_MANAGER.objects_descriptions,
        )

    def describe_logs(self) -> Matrix:
        """Describe the log sources within a solution.

        Returns:
            Matrix: Matrix containing log sources details
        """
        return describe_solution_objects(
            self.solution.LOGS_MANAGER.KEYS_DESCRIPTIONS,
            self.solution.LOGS_MANAGER.objects_descriptions,
        )

    def describe_actions(self) -> Matrix:
        """Describe the actions within a solution.

        Returns:
            Matrix: Matrix containing actions details
        """
        return describe_solution_objects(
            self.solution.ACTIONS_MANAGER.KEYS_DESCRIPTIONS,
            self.solution.ACTIONS_MANAGER.objects_descriptions,
        )


def describe_solution_objects(
    keys_descriptions: KeysDescriptions,
    generic_objects_descriptions: BaseGenericObjectsDescriptions,
    concrete_objects: typing.Optional[BaseConcreteResultObjects] = None,
) -> Matrix:
    """Describe multiple objects from a solution.

    Args:
        keys_descriptions (KeysDescriptions): Descriptions for all keys
        generic_objects_descriptions (BaseGenericObjectsDescriptions):
            Descriptions for all generic objects
        concrete_objects (BaseConcreteResultObjects): Objects containing the
            concrete values. Defaults to None.

    Returns:
        Matrix: Matrix describing the objects
    """
    matrix = []

    # Create the header
    headers = list(keys_descriptions.values())
    if concrete_objects:
        headers.append("Value")
    matrix.append(headers)

    # Create the body
    entries = []
    keys_ids = list(keys_descriptions.keys())
    id_key = keys_ids[0]
    if concrete_objects:
        for key, value in concrete_objects.items():
            description = [
                elem
                for elem in generic_objects_descriptions
                if elem[id_key] == key
            ][0]

            row = [to_str(elem) for elem in description.values()]
            row.append(to_str(value))
            entries.append(row)
    else:
        for current_object in generic_objects_descriptions:
            row = []
            for key in keys_ids:
                row.append(to_str(current_object[key]))

            entries.append(row)

    # Sort the entries
    entries.sort(key=lambda entry: entry[0])

    matrix.extend(entries)

    return matrix


def describe_solution_object(
    keys_descriptions: KeysDescriptions,
    generic_objects_descriptions: BaseGenericObjectsDescriptions,
    key: str,
) -> Matrix:
    """Describe a single object of a solution.

    Args:
        keys_descriptions (KeysDescriptions): Descriptions for all keys
        generic_objects_descriptions (BaseGenericObjectsDescriptions):
            Descriptions for all generic objects
        key (str): Key to describe

    Returns:
        Matrix: Matrix describing the object
    """
    keys = list(keys_descriptions.values())
    id_key = list(keys_descriptions.keys())[0]

    description = [
        elem for elem in generic_objects_descriptions if elem[id_key] == key
    ][0]
    values = [to_str(elem) for elem in description.values()]

    return [[key, value] for key, value in zip(keys, values)]
