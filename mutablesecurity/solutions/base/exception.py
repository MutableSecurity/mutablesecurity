"""Module defining a parent solution exception."""
from mutablesecurity.helpers.exceptions import SolutionException


class BaseSolutionException(SolutionException):
    """Exception to be used as a parent by the solutions' implementations."""
