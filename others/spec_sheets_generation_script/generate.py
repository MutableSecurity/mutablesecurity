#!/usr/bin/env python3

"""Python 3 script for generating all the spec sheets for solutions.

This script requires to be ran with:
    poetry run <path_to_script> <dump_folder>.
"""

import json
import os
import sys
import typing

from mutablesecurity.autodoc.solution_spec_sheet import (
    SolutionSpecSheet,
    generate_all_sheets,
)

INDEX_FILENAME = "solutions.json"


def __generate_sheet_full_path(dump_folder: str, identifier: str) -> str:
    return os.path.join(dump_folder, identifier + ".md")


def __dump_documentation(dump_folder: str, sheet: SolutionSpecSheet) -> None:
    with open(dump_folder, "w", encoding="utf-8") as output_file:
        output_file.write(sheet.md_spec_sheet)


def __dump_index_with_general_info(
    dump_folder: str, general_info: typing.List[dict]
) -> None:
    json_general_data = json.dumps(general_info)

    full_path = os.path.join(dump_folder, INDEX_FILENAME)
    with open(full_path, "w", encoding="utf-8") as output_file:
        output_file.write(json_general_data)


def main() -> None:
    """Run the main graph generation functionality."""
    if len(sys.argv) != 2:
        exit()
    dump_folder = sys.argv[1]

    general_info = []
    for sheet in generate_all_sheets():
        general_info.append(sheet.general_info)

        dump_full_path = __generate_sheet_full_path(
            dump_folder, sheet.solution_id
        )
        __dump_documentation(dump_full_path, sheet)

    __dump_index_with_general_info(dump_folder, general_info)


if __name__ == "__main__":
    main()
