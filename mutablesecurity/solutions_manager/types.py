"""Module for storing types useful in the parent package's modules."""
import typing

from mutablesecurity.solutions.base import BaseSolution

SolutionsList = typing.List[BaseSolution]
SolutionsGenerator = typing.Generator[BaseSolution, None, None]
BaseSolutionType = typing.Type[BaseSolution]
