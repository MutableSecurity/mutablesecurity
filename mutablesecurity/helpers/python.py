"""Module for processing Python code."""
import ast
import inspect
import typing


def __execute_for_each_function_in_class(
    haystack_class: typing.Type[object], visit_function: typing.Callable
) -> typing.List[typing.Any]:
    result = []

    def __visit(node: ast.FunctionDef) -> None:
        current_result = visit_function(node)
        if current_result:
            result.append(current_result)

    visitor = ast.NodeVisitor()
    visitor.visit_FunctionDef = __visit  # type: ignore[assignment]
    visitor.visit(
        compile(
            inspect.getsource(haystack_class), "?", "exec", ast.PyCF_ONLY_AST
        )
    )

    return result


def find_public_methods(
    haystack_class: typing.Type[object],
) -> typing.List[str]:
    """Traverse a class to find its public methods.

    Args:
        haystack_class (typing.Type[object]): Class to look in

    Returns:
        typing.List[str]: List of methods' names
    """

    def __visit(node: ast.FunctionDef) -> typing.Optional[str]:
        name = node.name
        if not name.startswith("_"):
            return name
        else:
            return None

    return __execute_for_each_function_in_class(haystack_class, __visit)


def find_decorated_methods(
    haystack_class: typing.Type[object], needle_decorator: str
) -> typing.List[str]:
    """Traverse a class to find decorated methods.

    Args:
        haystack_class (typing.Type[object]): Class to look in
        needle_decorator (str): Searched decorator

    Returns:
        typing.List[str]: List of methods' names
    """

    def __visit(node: ast.FunctionDef) -> typing.Optional[str]:
        for subnode in node.decorator_list:
            ast_dump = ast.dump(subnode)

            if f"id='{needle_decorator}'" in ast_dump:
                return node.name

        return None

    visitor = ast.NodeVisitor()
    visitor.visit_FunctionDef = __visit  # type: ignore[assignment]
    visitor.visit(
        compile(
            inspect.getsource(haystack_class), "?", "exec", ast.PyCF_ONLY_AST
        )
    )

    return __execute_for_each_function_in_class(haystack_class, __visit)
