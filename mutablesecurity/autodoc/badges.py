"""Module for generating badges with shields.io."""


from mutablesecurity.helpers.colors import Color
from mutablesecurity.solutions.base import SolutionMaturityLevels


class Badge:
    """Class modeling a badge."""

    title: str
    text: str
    color: Color

    def __init__(self, title: str, text: str, color: Color) -> None:
        """Initialize the instance.

        Args:
            title (str): Title, namely the left part of the badge
            text (str): Text, namely the right part of the badge
            color (Color): Color
        """
        self.title = title
        self.text = text
        self.color = color

    def __url_encode(self, text: str) -> str:
        return text.replace(" ", "%20")

    def export_as_html(self) -> str:
        """Export the badge as HTML code.

        Returns:
            str: String representation
        """
        title_encoded = self.__url_encode(self.title)
        text_encoded = self.__url_encode(self.text)
        color = self.color.badge_io_color

        return (
            f"<img alt='{self.title}: {self.text}'"
            f" src='https://img.shields.io/badge/{title_encoded}"
            f"-{text_encoded}-{color}?style=flat-square'>"
        )


class MaturityLevelBadge(Badge):
    """Badge representing the maturity level of a solution."""

    def __init__(self, level: SolutionMaturityLevels) -> None:
        """Initialize the instance.

        Args:
            level (SolutionMaturityLevels): Maturity level
        """
        super().__init__("Maturity", str(level), level.value.color)
