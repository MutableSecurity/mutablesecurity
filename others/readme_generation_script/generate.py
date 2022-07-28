#!/usr/bin/env python3

"""Python 3 script for generating README.md based on repository's content.

This script requires to be ran with:
    poetry run <path_to_script>.
"""

import typing
from functools import cmp_to_key

from mutablesecurity.solutions.base import BaseSolution, SolutionMaturity
from mutablesecurity.solutions_manager import SolutionsManager

BaseSolutionType = typing.Type[BaseSolution]

MATURITY_ORDER = [
    SolutionMaturity.PRODUCTION,
    SolutionMaturity.REFACTORING,
    SolutionMaturity.UNDER_DEVELOPMENT,
]
MATURITY_COLOR_MAPPING = {
    SolutionMaturity.PRODUCTION: "blightgreen",
    SolutionMaturity.REFACTORING: "yellowgreen",
    SolutionMaturity.UNDER_DEVELOPMENT: "red",
}
TEMPLATE_PATH = "others/readme_generation/README.template.md"
README_PATH = "README.md"
ROW_FORMAT = """        <tr>
            <td>
                <a href="{link}">
                    <img src="others/readme_images/solutions/{image_id}.webp">
                </a>
            </td>
            <td>{description}</td>
            <td>
                <img alt="Status: {text_status}" src="https://img.shields.io/\
badge/Status-{text_status_encoded}-{status_color}?style=flat-square">
            </td>
        </tr>"""


def get_non_dev_solutions() -> typing.Generator[BaseSolutionType, None, None]:
    """Get all non-development solutions.

    Yields:
        Iterator[typing.Generator[BaseSolutionType, None, None]]: Solution
    """
    manager = SolutionsManager()

    for solution_id in manager.get_available_solutions_ids():
        solution = manager.get_solution_by_id(solution_id)

        if solution.MATURITY != SolutionMaturity.DEV_ONLY:
            yield solution


def get_ordered_non_dev_solutions() -> typing.List[BaseSolutionType]:
    """Get all non-development solutions, ordered by maturity.

    Returns:
        typing.List[BaseSolutionType]: Maturity-ordered solutions
    """

    def maturity_compare(
        first: BaseSolutionType, second: BaseSolutionType
    ) -> int:
        order = MATURITY_ORDER

        return order.index(first.MATURITY) - order.index(second.MATURITY)

    solutions = list(get_non_dev_solutions())
    solutions.sort(key=cmp_to_key(maturity_compare))

    return solutions


def get_maturity_badge_color(maturity: SolutionMaturity) -> str:
    """Translate a badge into its corresponding color.

    Args:
        maturity (SolutionMaturity): Maturity level

    Returns:
        str: Color identifier
    """
    return MATURITY_COLOR_MAPPING[maturity]


def space_encode_for_badges(text: str) -> str:
    """Replace the spaces in badge's text.

    Args:
        text (str): Text to process

    Returns:
        str: Processed text
    """
    return text.replace(" ", "%20")


def generate_table_rows() -> typing.Generator[str, None, None]:
    """Generate a row for each non-development solution.

    Yields:
        Iterator[typing.Generator[str, None, None]]: Row
    """
    for solution in get_ordered_non_dev_solutions():
        link = solution.REFERENCES[0]
        image_id = solution.IDENTIFIER
        description = solution.DESCRIPTION
        text_status = str(solution.MATURITY)
        text_status_encoded = space_encode_for_badges(text_status)
        status_color = get_maturity_badge_color(solution.MATURITY)

        yield ROW_FORMAT.format(
            link=link,
            image_id=image_id,
            description=description,
            text_status=text_status,
            text_status_encoded=text_status_encoded,
            status_color=status_color,
        )


def create_readme(entries: typing.List[str]) -> None:
    """Create a README.md in repository's root, based on some HTML table rows.

    Args:
        entries (typing.List[str]): HTML table rows
    """
    rows = "\n".join(entries)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as template_readme:
        content = template_readme.read()
        readme_content = content.format(solutions_rows=rows)

    with open(README_PATH, "w", encoding="utf-8") as readme:
        readme.write(readme_content)


def main() -> None:
    """Run the main functionality."""
    entries = list(generate_table_rows())

    create_readme(entries)


if __name__ == "__main__":
    main()
