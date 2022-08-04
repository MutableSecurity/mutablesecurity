#!/usr/bin/env python3

"""Python 3 script for generating README.md based on repository's content.

This script requires to be ran with:
    poetry run <path_to_script>.
"""


from mutablesecurity.autodoc import SolutionsStatusesTable

TEMPLATE_PATH = "others/readme_generation_script/README.template.md"
README_PATH = "README.md"


def main() -> None:
    """Run the main functionality."""
    solutions_status_table = SolutionsStatusesTable().export_as_html()

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as template_readme:
        content = template_readme.read()
        readme_content = content.format(
            solutions_status_table=solutions_status_table
        )

    with open(README_PATH, "w", encoding="utf-8") as readme:
        readme.write(readme_content)


if __name__ == "__main__":
    main()
