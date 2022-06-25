"""Module for defining deployments and their results."""

import typing
from enum import Enum


class ResponseTypes(Enum):
    """Class enumerating the response types."""

    SUCCESS = 0
    ERROR = 1


class SecurityDeploymentResult:
    """Class encapsulating the result of a deployment."""

    host: str
    response_type: ResponseTypes
    message: str
    additional_data: typing.Any

    def __init__(
        self,
        host: str,
        response_type: ResponseTypes,
        message: str,
        additional_data: typing.Any,
    ) -> None:
        """Initialize the object.

        Args:
            host (str): String identifier of the host
            response_type (ResponseTypes): Type of result
            message (str): Result's message
            additional_data (typing.Any): Additional data accompanying the
                result
        """
        self.host = host
        self.response_type = response_type
        self.message = message
        self.additional_data = additional_data
