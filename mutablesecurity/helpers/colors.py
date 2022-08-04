"""Module defining colors exposed by shields.io."""


class Color:
    """Color."""

    badge_io_color: str

    def __init__(self, badge_io_color: str) -> None:
        """Initialize the instance.

        Args:
            badge_io_color (str): badge.io color name
        """
        self.badge_io_color = badge_io_color


BrightGreenColor = Color("blightgreen")
YellowGreenColor = Color("yellowgreen")
RedColor = Color("red")
LightGreyColor = Color("lightgrey")
