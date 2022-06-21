"""Module for storing printed in the CLI."""

from enum import Enum

from rich.emoji import Emoji
from rich.text import Text

from ..helpers.exceptions import CLIException


class MessageTypes(Enum):
    """Types of messages."""

    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    QUESTION = "white_question_mark"


class Message:
    """Class for storing types of messages used in the CLI."""

    message_type: MessageTypes
    severity: int
    emoji: Emoji
    message: Text

    def __init__(
        self,
        message_type: MessageTypes,
        severity: int,
        emoji_id: str,
        message: str,
    ) -> None:
        """Initialize the object.

        Args:
            message_type (MessageTypes): Type
            severity (int): Numerical severity level
            emoji_id (str): Rich emoji identifier
            message (str): Message
        """
        self.message_type = message_type
        self.severity = severity
        self.emoji = Emoji(emoji_id)
        self.message = Text(message)

    def __justify_long_text(self) -> None:
        """Prepare a long text for printing."""
        self.message = Text(str(self.message), justify="full")

    def to_text(self, justified: bool = True) -> Text:
        """Convert the message into its rich representation.

        Args:
            justified (bool): Boolean indicating if the text is long and needs
                to be justified before returned

        Returns:
            Text: rich representation
        """
        if justified:
            self.__justify_long_text()

        result = Text()
        result.append(str(self.emoji))
        result.append(" ")
        result.append(self.message)

        return result


class MessageFactory:
    """Factory for creating CLI messages."""

    def create_message(
        self, message_type: MessageTypes, message: str
    ) -> Message:
        """Create a message based on its type.

        Raises:
            UnknownMessageTypeException: The provided type is unknown.

        Args:
            message_type (MessageTypes): Type of message
            message (str): Message

        Returns:
            Message: Constructed message
        """
        if message_type == MessageTypes.WARNING:
            return Message(message_type, 0, "warning", message)
        elif message_type == MessageTypes.ERROR:
            return Message(message_type, 10, "stop_sign", message)
        elif message_type == MessageTypes.ERROR:
            return Message(message_type, 20, "white_check_mark", message)
        else:
            raise UnknownMessageTypeException()


class UnknownMessageTypeException(CLIException):
    """The provided message type is unknown."""
