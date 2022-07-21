"""Module for defining deployments and their results."""

from __future__ import annotations

import typing
from enum import Enum

if typing.TYPE_CHECKING:
    from mutablesecurity.solutions.base import ConcreteObjectsResult


class ResponseTypes(Enum):
    """Class enumerating the response types."""

    SUCCESS = 0
    ERROR = 1


class SecurityDeploymentResult:
    """Class encapsulating the result of a deployment."""

    host_id: str
    response_type: ResponseTypes
    message: str
    additional_data: typing.Optional[ConcreteObjectsResult]

    def __init__(
        self,
        host_id: str,
        response_type: ResponseTypes,
        message: str,
        additional_data: typing.Optional[ConcreteObjectsResult] = None,
    ) -> None:
        """Initialize the object.

        Args:
            host_id (str): String identifier of the host
            response_type (ResponseTypes): Type of result
            message (str): Result's message
            additional_data (ConcreteObjectsResult): Additional data
                accompanying the result. Defaults to None.
        """
        self.host_id = host_id
        self.response_type = response_type
        self.message = message
        if additional_data:
            self.additional_data = additional_data
