"""Module for testing the Python helper module."""

from src.helpers.python import find_decorated_methods


class ClassWithStaticMethods:
    """Class with static methods."""

    class_member: bool = False
    instance_member: bool

    def __init__(self) -> None:
        """Initialize the instance's member."""
        self.instance_member = False

    @staticmethod
    def set_class_member() -> None:
        """Set the class' member."""
        ClassWithStaticMethods.class_member = True

    @staticmethod
    def unset_class_member() -> None:
        """Unset the class' member."""
        ClassWithStaticMethods.class_member = False

    def set_instance_member(self) -> None:
        """Set the instance's member."""
        self.instance_member = True

    def unset_instance_member(self) -> None:
        """Unsets the instance's member."""
        self.instance_member = False


def test_find_decorated_methods() -> None:
    """Test the finding of decorated functions."""
    methods = find_decorated_methods(ClassWithStaticMethods, staticmethod)

    for static_method in ["set_class_member", "unset_class_member"]:
        assert (
            static_method in methods
        ), f"Method {static_method} was not detected as decorated."
