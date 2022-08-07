"""Module generating an HTML table with information about production solutions.

The only included information are:
- Name
- Description
- Badges.
"""

import typing

from mutablesecurity.autodoc import MaturityLevelBadge
from mutablesecurity.solutions_manager import SolutionsManager

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
                {maturity_badge}
            </td>
        </tr>"""


def __generate_rows() -> typing.Generator[str, None, None]:
    solutions = (
        SolutionsManager().get_non_dev_solutions_sorted_desc_by_maturity()
    )

    for solution in solutions:
        link = solution.REFERENCES[0]
        image_id = solution.IDENTIFIER
        description = solution.DESCRIPTION
        text_maturity = str(solution.MATURITY)
        badge_code = MaturityLevelBadge(solution.MATURITY).export_as_html()

        yield ROW_FORMAT.format(
            link=link,
            image_id=image_id,
            description=description,
            text_maturity=text_maturity,
            maturity_badge=badge_code,
        )


def generate_solutions_statuses_table() -> str:
    """Generate_the solutions statuses_table.

    Returns:
        str: HTML representation of the table
    """
    entries = list(__generate_rows())

    return TABLE.format(solutions_rows="".join(entries))
