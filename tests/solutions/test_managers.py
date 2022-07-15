"""Module for testing the actions and their management."""
from mutablesecurity.solutions.base.action import ActionsManager
from mutablesecurity.solutions.base.information import InformationManager
from mutablesecurity.solutions.base.log import LogsManager
from mutablesecurity.solutions.base.test import TestsManager
from mutablesecurity.solutions.implementations.dummy.code import (
    AppendToFileAction,
    ContentLogs,
    CurrentUserInformation,
    FileSizeInformation,
    PresenceTest,
    UbuntuRequirement,
)


def test_common_functionality_in_managers() -> None:
    """Test the common functionality in all the managers."""
    actions = [AppendToFileAction]
    information = [CurrentUserInformation, FileSizeInformation]
    tests = [PresenceTest, UbuntuRequirement]
    logs = [ContentLogs]
    objects = [actions, information, tests, logs]

    actions_manager = ActionsManager(actions)
    information_manager = InformationManager(information)
    tests_manager = TestsManager(tests)
    logs_manager = LogsManager(logs)
    managers = [
        actions_manager,
        information_manager,
        tests_manager,
        logs_manager,
    ]

    for current_objects, current_manager in zip(objects, managers):
        # Test the returned types
        first_object = current_manager.get_object_by_identifier(
            current_objects[0].IDENTIFIER
        )
        assert (
            first_object == current_objects[0]
        ), f"Invalid type returned by the manager {current_manager}"

        # Test the representations
        representation = current_manager.represent_as_matrix()
        id_to_find = current_objects[0].IDENTIFIER
        present = False
        for line in representation:
            for element in line:
                if element == id_to_find:
                    present = True
                    break

            if present:
                break
        assert present, (
            "The action identifier is not present in the matrix"
            f" representation of {current_manager}."
        )
