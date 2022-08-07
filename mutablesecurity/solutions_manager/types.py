"""Module for storing types useful in the parent package's modules."""
import typing

from mutablesecurity.solutions.base import BaseSolutionType

SolutionsList = typing.List[BaseSolutionType]
SolutionsGenerator = typing.Generator[BaseSolutionType, None, None]
BaseSolutionType = typing.Type[BaseSolutionType]
