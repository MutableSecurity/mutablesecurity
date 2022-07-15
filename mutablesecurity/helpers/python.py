"""Module for processing Python code."""
import ast
import inspect
import typing


def find_decorated_methods(
    haystack_class: typing.Type[object], needle_decorator: typing.Callable
) -> typing.List[str]:
    """Traverse a class to find decorated methods.

    Args:
        haystack_class (typing.Type[object]): Class to look in
        needle_decorator (typing.Callable): Searched decorator

    Returns:
        typing.List[str]: List of methods' names
    """
    found_function = []

    def __visit(node: ast.FunctionDef) -> None:
        for subnode in node.decorator_list:
            ast_dump = ast.dump(subnode)

            if f"id='{needle_decorator.__name__}'" in ast_dump:
                found_function.append(node.name)
                return

    visitor = ast.NodeVisitor()
    visitor.visit_FunctionDef = __visit  # type: ignore
    visitor.visit(
        compile(
            inspect.getsource(haystack_class), "?", "exec", ast.PyCF_ONLY_AST
        )
    )

    return found_function
