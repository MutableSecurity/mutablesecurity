"""Module generating an HTML table with information about production solutions.

The only included information are:
- Name
- Description
- Badges.
"""

import typing

from mutablesecurity.autodoc import MaturityLevelBadge
from mutablesecurity.solutions.base import BaseSolution, SolutionMaturityLevels
from mutablesecurity.solutions_manager import (
    SolutionsFilter,
    SolutionsManager,
    SolutionsSorter,
)

TABLE = """<table>
    <thead>
        <tr>
            <th>Solution</th>
            <th>Description</th>
            <th>Others</th>
        </tr>
    </thead>
    <tbody>
{solutions_rows}
        <tr>
            <td colspan=3><center>More coming soon...</center></td>
        </tr>
    </tbody>
</table>"""

ROW_FORMAT = """\
        <tr>
            <td>
                <a href="{link}">
                    <img src="others/readme_images/solutions/{image_id}.webp">
                </a>
            </td>
            <td>{description}</td>
            <td>
                {status_badge}
            </td>
        </tr>"""


class SolutionsStatusesTable:
    """Class generating a table with integrated solutions' statuses."""

    def __get_sorted_non_dev_solutions(self) -> typing.List[BaseSolution]:
        solutions = SolutionsManager().get_production_solutions()
        non_dev_solutions = list(
            SolutionsFilter(solutions).had_not_maturity_level(
                SolutionMaturityLevels.DEV_ONLY
            )
        )

        return SolutionsSorter(non_dev_solutions).by_maturity(ascending=False)

    def __generate_rows(self) -> typing.Generator[str, None, None]:
        for solution in self.__get_sorted_non_dev_solutions():
            link = solution.REFERENCES[0]
            image_id = solution.IDENTIFIER
            description = solution.DESCRIPTION
            text_status = str(solution.MATURITY)
            badge_code = MaturityLevelBadge(solution.MATURITY).export_as_html()

            yield ROW_FORMAT.format(
                link=link,
                image_id=image_id,
                description=description,
                text_status=text_status,
                status_badge=badge_code,
            )

    def export_as_html(self) -> str:
        """Export the table as HTML code.

        Returns:
            str: HTML representation of the table
        """
        entries = list(self.__generate_rows())

        return TABLE.format(solutions_rows="".join(entries))
