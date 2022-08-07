#!/usr/bin/env python3

"""Python 3 script for generating a call graph from inside the solution API.

Before running this, make sure you have graphviz installed locally:
- On Windows: choco install -y graphviz
- On Linux: apt install graphviz.

This script requires to be ran with:
    poetry run <path_to_script>.

References:
- https://gist.github.com/jargnar/0946ab1d985e2b4ab776
"""

import ast
import os
import typing
from collections import deque

import graphviz

SOLUTION_API_PATH = "mutablesecurity/solutions/base/solution.py"
SKIPPED_FUNCTION = ["__init_subclass__"]
EXPORT_FOLDER = "exports"


class FuncCallVisitor(ast.NodeVisitor):
    """Class for visiting calls in an abstract syntax tree."""

    # The methods needs to have the name of parent's methods.
    # pylint: disable=invalid-name

    _name: deque

    def __init__(self) -> None:
        """Initialize the instance."""
        self._name = deque()

    @property
    def name(self) -> str:
        """Get the constructed call name.

        Returns:
            str: Name
        """
        return ".".join(self._name)

    @name.deleter
    def name(self) -> None:
        """Delete the constructed name."""
        self._name.clear()

    def visit_Name(self, node: ast.Name) -> None:  # noqa: N802
        """Visit node's name.

        Args:
            node (ast.AST): Current node
        """
        self._name.appendleft(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> None:  # noqa: N802
        """Visit node's attributes.

        Args:
            node (ast.AST): Current node
        """
        try:
            self._name.appendleft(node.attr)
            self._name.appendleft(node.value.id)  # type: ignore[attr-defined]
        except AttributeError:
            self.generic_visit(node)


def get_cls_func_calls(tree: ast.AST) -> typing.List[str]:
    """Get class definition from an AST.

    Args:
        tree (ast.AST): Abstract syntax tree of a source file

    Returns:
        typing.List[str]: List of functions defines
    """
    func_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            visitor = FuncCallVisitor()
            visitor.visit(node.func)

            # Removes the prefix of and return only the class methods
            if visitor.name.startswith("cls."):
                prefix_len = len("cls.")
                name: str = visitor.name[prefix_len:]
                func_calls.append(name)

    return func_calls


def get_functions_defines(
    tree: ast.Module,
) -> typing.Generator[ast.FunctionDef, None, None]:
    """Traverse the BaseSolution definition to get its function definitions.

    Args:
        tree (ast.Module): Abstract syntax tree of the BaseSolution class

    Yields:
        typing.Generator[ast.FunctionDef, None, None]: Generator of function
            definitions
    """
    # Get the class definition
    class_def = [
        elem
        for elem in tree.body
        if isinstance(elem, ast.ClassDef) and elem.name == "BaseSolution"
    ][0]

    # Get the function definitions
    for elem in class_def.body:
        if isinstance(elem, ast.FunctionDef):
            yield elem


def get_calls(
    source: str,
) -> typing.Generator[typing.Tuple[str, typing.List[str]], None, None]:
    """Get the calls of each filtered function definition.

    Args:
        source (str): Python source

    Yields:
        Iterator[typing.Generator[typing.Tuple[str, typing.List[str]], None, \
            None]]: Generator of tuples, with elements being the caller and all
            the called functions
    """
    ast_tree = ast.parse(source)

    for function_def in get_functions_defines(ast_tree):
        if function_def.name in SKIPPED_FUNCTION:
            continue

        yield (function_def.name, get_cls_func_calls(function_def))


def create_graph(
    cli_commands: typing.List[str],
    abstract_methods: typing.List[str],
    class_methods: typing.List[str],
    managers_methods: typing.List[str],
    calls: typing.List[typing.Tuple[str, str]],
) -> None:
    """Create and export a call graph for BaseSolution.

    Args:
        cli_commands (typing.List[str]): Exported CLI commands
        abstract_methods (typing.List[str]): Abstract methods, that needs to be
            overwritten in the solutions implementations
        class_methods (typing.List[str]): Methods already implemented in the
            BaseSolution
        managers_methods (typing.List[str]): Methods of managers (for example,
            information, logs, etc.)
        calls (typing.List[typing.Tuple[str, str]]): List of tuples of caller-
            callee
    """
    # Create the graph
    call_graph = graphviz.Digraph(
        name="Call Graph",
        comment="Call Graph in Solution API",
        filename="call_graph",
        format="png",
        graph_attr={"nodesep": "3", "ranksep": "3"},
    )

    # Add the CLI commands
    with call_graph.subgraph(name="cluster_cli_commands") as cli_graph:
        cli_graph.attr(label="CLI Commands")
        cli_graph.attr(color="red")
        cli_graph.attr("node", shape="box", style="filled", color="red")
        for command in cli_commands:
            cli_graph.node(command, command)

    # Add the abstract methods
    with call_graph.subgraph(
        name="cluster_abstract_methods"
    ) as abstract_graph:
        abstract_graph.attr(label="Abstract methods")
        abstract_graph.attr(
            "node", shape="box", style="filled", color="royalblue"
        )
        for method in abstract_methods:
            abstract_graph.node(method, method)

    # Add the class methods
    with call_graph.subgraph(name="cluster_class_methods") as class_graph:
        class_graph.attr(label="Concrete class methods")
        class_graph.attr(
            "node", shape="box", style="filled", color="lightslategray"
        )
        for method in class_methods:
            class_graph.node(method, method)

    # Add the managers methods
    with call_graph.subgraph(
        name="cluster_managers_methods"
    ) as managers_graph:
        managers_graph.attr(label="Managers methods")
        managers_graph.attr(
            "node", shape="ellipse", style="filled", color="lightgray"
        )
        for method in managers_methods:
            managers_graph.node(method, method)

    # Add the edges
    for call in calls:
        call_graph.edge(*call)

    # Export the PNG file
    export_folder = os.path.join(os.path.dirname(__file__), EXPORT_FOLDER)
    call_graph = call_graph.unflatten(stagger=3)
    call_graph.render(directory=export_folder)


def get_all_calls(
    source: str,
) -> typing.Tuple[
    typing.List[str],
    typing.List[str],
    typing.List[str],
    typing.List[str],
    typing.List[typing.Tuple[str, str]],
]:
    """Get all methods (by type) and calls from a Python source.

    Args:
        source (str): Python source

    Returns:
        typing.Tuple[ typing.List[str], typing.List[str], typing.List[str], \
            typing.List[str], typing.List[typing.Tuple[str, str]]]: Tuple of
            CLI commands,abstract methods, methods implemented in BaseSolution,
            methods of managers and effective calls
    """
    cli_commands = []
    abstract_methods = []
    class_methods = []
    managers_methods = set()
    calls = []

    for name, func_calls in get_calls(source):
        if name.startswith("__"):
            class_methods.append(name)
        elif name.startswith("_"):
            abstract_methods.append(name)
        else:
            cli_commands.append(name)

        # Traverse the calls made in the class function
        for call in func_calls:
            # Check if a new manager is involved
            if "." in call:
                managers_methods.add(call)

            calls.append((name, call))

    return (
        cli_commands,
        abstract_methods,
        class_methods,
        list(managers_methods),
        calls,
    )


def main() -> None:
    """Run the main graph generation functionality."""
    with open(SOLUTION_API_PATH, "r", encoding="utf-8") as source_file:
        source = source_file.read()
        methods_and_calls = get_all_calls(source)
        create_graph(*methods_and_calls)


if __name__ == "__main__":
    main()
