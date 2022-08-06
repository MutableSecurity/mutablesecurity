#!/usr/bin/env python3

"""Python 3 script for generating all the spec sheets for solutions.

This script requires to be ran with:
    poetry run <path_to_script> <dump_folder>.
"""

import os
import sys

from mutablesecurity.autodoc.solution_spec_sheet import generate_all_sheets


def __generate_sheet_full_path(dump_folder: str, identifier: str) -> str:
    return os.path.join(dump_folder, identifier + ".md")


def main() -> None:
    """Run the main graph generation functionality."""
    if len(sys.argv) != 2:
        exit()

    dump_folder = sys.argv[1]
    for sheet in generate_all_sheets():
        identifier = sheet.solution_id

        dump_full_path = __generate_sheet_full_path(dump_folder, identifier)
        with open(dump_full_path, "w", encoding="utf-8") as output_file:
            output_file.write(sheet.md_spec_sheet)


if __name__ == "__main__":
    main()
