"""Module generating Markdown +_ HTML spec sheets for solution."""

import re
import typing

from mutablesecurity.helpers.html import generate_code_block, generate_table
from mutablesecurity.helpers.markdown import (
    generate_link,
    generate_unordered_list,
)
from mutablesecurity.helpers.type_hints import StringMatrix
from mutablesecurity.solutions.base import BaseSolution, SolutionCategories
from mutablesecurity.solutions_manager import SolutionsManager
from mutablesecurity.visual_proxy import ObjectsDescriberFacade

SPEC_SHEET_TEMPLATE = """\
# {name}

## Metadata

- **Identifier**: {identifier}
- **Maturity**: {maturity}

## Description

{description}

## Categories

{categories_list}

## Actions

{actions_table}

## Information

{information_table}

## Logs

{logs_table}

## Tests

{tests_table}

## References

{references_list}
"""


class SolutionSpecSheet:
    """Data structure modeling a spec sheet for a solution."""

    solution_id: str
    md_spec_sheet: str

    def __init__(self, solution_id: str, md_spec_sheet: str) -> None:
        """Initialize the instance.

        Args:
            solution_id (str): Solution identifier
            md_spec_sheet (str): String representing the spec sheet
        """
        self.solution_id = solution_id
        self.md_spec_sheet = md_spec_sheet


def generate_all_sheets() -> typing.Generator[SolutionSpecSheet, None, None]:
    """Generate sheets for all production modules.

    Yields:
        Iterator[typing.Generator[SolutionSpecSheet, None, None]]: Sheet
    """
    solutions = (
        SolutionsManager().get_non_dev_solutions_sorted_desc_by_maturity()
    )

    for solution in solutions:
        md_content = __generate_solution_spec_sheet(solution)

        yield SolutionSpecSheet(solution.IDENTIFIER, md_content)


def __generate_solution_spec_sheet(solution: BaseSolution) -> str:
    details = __generate_format_details(solution)

    return SPEC_SHEET_TEMPLATE.format(**details)


def __generate_format_details(solution: BaseSolution) -> dict:
    categories_list = __generate_categories_list(solution.CATEGORIES)
    references_list = __generate_references_list(solution.REFERENCES)
    actions_table = __generate_actions_html_table(solution)
    information_table = __generate_information_html_table(solution)
    logs_table = __generate_logs_html_table(solution)
    tests_table = __generate_tests_html_table(solution)

    return {
        "name": solution.FULL_NAME,
        "identifier": solution.IDENTIFIER,
        "maturity": solution.MATURITY,
        "description": solution.DESCRIPTION,
        "categories_list": categories_list,
        "actions_table": actions_table,
        "information_table": information_table,
        "logs_table": logs_table,
        "tests_table": tests_table,
        "references_list": references_list,
    }


def __generate_categories_list(
    categories: typing.List[SolutionCategories],
) -> str:
    string_categories = [str(category) for category in categories]

    return generate_unordered_list(string_categories)


def __generate_references_list(
    references: typing.List[str],
) -> str:
    md_references = [
        generate_link(reference, reference) for reference in references
    ]

    return generate_unordered_list(md_references)


def __generate_actions_html_table(solution: BaseSolution) -> str:
    actions_matrix = ObjectsDescriberFacade(solution).describe_actions()
    actions_matrix = __mark_cells_as_code(actions_matrix)

    return generate_table(actions_matrix)


def __generate_information_html_table(solution: BaseSolution) -> str:
    information_matrix = ObjectsDescriberFacade(
        solution
    ).describe_information()
    information_matrix = __mark_cells_as_code(information_matrix)

    return generate_table(information_matrix)


def __generate_logs_html_table(solution: BaseSolution) -> str:
    logs_matrix = ObjectsDescriberFacade(solution).describe_logs()
    logs_matrix = __mark_cells_as_code(logs_matrix)

    return generate_table(logs_matrix)


def __generate_tests_html_table(solution: BaseSolution) -> str:
    tests_matrix = ObjectsDescriberFacade(solution).describe_tests()
    tests_matrix = __mark_cells_as_code(tests_matrix)

    return generate_table(tests_matrix)


def __mark_cells_as_code(matrix: StringMatrix) -> StringMatrix:
    columns_count = len(matrix[0])

    for column_id in range(columns_count):
        if __check_if_column_contains_code(matrix, column_id):
            matrix = __mark_cells_from_column_as_code(matrix, column_id)

    return matrix


def __check_if_column_contains_code(
    matrix: StringMatrix, column_id: int
) -> bool:
    return matrix[0][column_id].lower() != "description"


def __mark_cells_from_column_as_code(
    matrix: StringMatrix, column_id: int
) -> StringMatrix:
    def __replace_with_code(match: re.Match) -> str:
        return generate_code_block(match.group())

    pattern = re.compile("([A-Za-z0-9_.]+)")

    row_count = len(matrix)
    for row_id in range(1, row_count):
        matrix[row_id][column_id] = pattern.sub(
            __replace_with_code, matrix[row_id][column_id]
        )

    return matrix
