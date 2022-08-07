"""Module translating data into HTML code."""

import typing

from mutablesecurity.helpers.type_hints import StringMatrix

TABLE_FORMAT = """\
<table>
    <thead>
        <tr>
{head}
        </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
</table>"""
HEAD_ENTRY_FORMAT = "            <th>{content}</th>"
ROW_FORMAT = """\
        <tr>
{cells}
        </tr>"""
EMPTY_TABLE_BODY = """\
        <tr>
            <td colspan="{columns_count}"><center>No entry yet</center></td>
        </tr>"""
CELL_FORMAT = "            <td>{content}</td>"
CODE_FORMAT = "<code>{code}</code>"


def generate_table(matrix: StringMatrix) -> str:
    """Generate an HTML table based on a matrix.

    Args:
        matrix (StringMatrix): Matrix to transform

    Returns:
        str: HTML code
    """
    head = matrix[0]
    body = matrix[1:]

    if len(body) == 0:
        columns_count = len(head)
        rows = __generate_empty_body(columns_count)
    else:
        rows = __generate_rows(body)

    return TABLE_FORMAT.format(head=__generate_head(head), rows=rows)


def __generate_empty_body(columns_count: int) -> str:
    return EMPTY_TABLE_BODY.format(columns_count=columns_count)


def __generate_head(raw_head: typing.List[str]) -> str:
    return "\n".join(
        [HEAD_ENTRY_FORMAT.format(content=entry) for entry in raw_head]
    )


def __generate_rows(raw_rows: StringMatrix) -> str:
    return "\n".join([__generate_row(row) for row in raw_rows])


def __generate_row(raw_row: typing.List[str]) -> str:
    cells = "\n".join([__generate_cell(cell) for cell in raw_row])

    return ROW_FORMAT.format(cells=cells)


def __generate_cell(cell: str) -> str:
    return CELL_FORMAT.format(content=cell)


def generate_code_block(code: str) -> str:
    """Generate HTML code block.

    Args:
        code (str): Text to highlight as code

    Returns:
        str: HTML code
    """
    return CODE_FORMAT.format(code=code)
