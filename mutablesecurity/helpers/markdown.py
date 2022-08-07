"""Module for generating Markdown code."""
import typing

UNORDERED_LIST_ITEM = "- {content}"
LINK_FORMAT = "[{caption}]({link})"
BOLD_FORMAT = "**{text}**"


def generate_unordered_list(items: typing.List[str]) -> str:
    """Generate an unordered list.

    Args:
        items (typing.List[str]): Lists items

    Returns:
        str: Markdown code
    """
    md_items = []
    for item in items:
        md_item = UNORDERED_LIST_ITEM.format(content=item)
        md_items.append(md_item)

    return "\n".join(md_items)


def generate_link(caption: str, link: str) -> str:
    """Generate a link.

    Args:
        caption (str): Caption, displayed in Markdown
        link (str): Effective link

    Returns:
        str: Markdown code
    """
    return LINK_FORMAT.format(caption=caption, link=link)
