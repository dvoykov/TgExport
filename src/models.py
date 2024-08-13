from typing import List, Optional
from datetime import datetime


class MsgReaction:
    """Represents a reaction to a message."""

    def __init__(
        self, chat_id: int, msg_id: int, user_id: int, dt: datetime, emoticon: str
    ):
        """
        Initializes a MsgReaction instance.
        """
        self.chat_id = chat_id
        self.msg_id = msg_id
        self.user_id = user_id
        self.dt = dt
        self.emoticon = emoticon

        self._validate()

    def _validate(self):
        """Validates the reaction data."""
        if not isinstance(self.chat_id, int):
            raise ValueError("Invalid chat Id")

        if not isinstance(self.msg_id, int) or self.msg_id <= 0:
            raise ValueError("Invalid msg Id")

        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("Invalid user Id")

        if not isinstance(self.dt, datetime):
            raise ValueError("Invalid datetime")

        if not isinstance(self.emoticon, str) or not self.emoticon:
            raise ValueError("Invalid emoticon")


class Msg:
    """Represents a message in a chat."""

    def __init__(
        self,
        chat_id: int,
        user_id: int,
        msg_id: int,
        msg_text: str,
        msg_dt: datetime,
        reply_to_msg_id: Optional[int],
        reactions: List[MsgReaction],
    ):
        """
        Initializes a Msg instance.

        Args:
            chat_id (int): The ID of the chat where the message was sent.
            user_id (int): The ID of the user who sent the message.
            msg_id (int): The ID of the message.
            msg_text (str): The text content of the message.
            msg_dt (datetime): The date and time when the message was sent.
            reply_to_msg_id (Optional[int]): The ID of the message to which this message is a reply, if any.
            reactions (List[MsgReaction]): A list of reactions to the message.
        """
        self.chat_id = chat_id
        self.user_id = user_id
        self.user_name = ""
        self.msg_id = msg_id
        self.msg_text = msg_text
        self.msg_dt = msg_dt
        self.reply_to_msg_id = reply_to_msg_id
        self.reactions = reactions if reactions is not None else []

        self._validate()

    def _validate(self):
        """Validates the message data."""
        if not isinstance(self.chat_id, int):
            raise ValueError("Invalid chat Id")

        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("Invalid user Id")

        if not isinstance(self.msg_id, int) or self.msg_id <= 0:
            raise ValueError("Invalid message Id")

        if not isinstance(self.msg_text, str) or not self.msg_text:
            raise ValueError("Invalid message text")

        if not isinstance(self.msg_dt, datetime):
            raise ValueError("Invalid datetime")

        if self.reply_to_msg_id is not None and (
            not isinstance(self.reply_to_msg_id, int) or self.reply_to_msg_id <= 0
        ):
            raise ValueError("Invalid reply-to message Id")

        if not isinstance(self.reactions, list):
            raise ValueError("Invalid reactions list")

        for reaction in self.reactions:
            if not isinstance(reaction, MsgReaction):
                raise ValueError("Invalid reaction object in reactions list")


class User:
    """Represents a Telegram user."""

    def __init__(
        self,
        chat_id: int,
        user_id: int,
        user_name: str,
        first_name: str,
        last_name: str,
    ):
        """
        Initializes a User instance.
        """
        self.chat_id = chat_id
        self.user_id = user_id
        self.user_name = user_name
        self.first_name = first_name
        self.last_name = last_name

        self._validate()

    def _validate(self):
        """Validates the reaction data."""
        if not isinstance(self.chat_id, int):
            raise ValueError("Invalid chat Id")

        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("Invalid user Id")

        if not isinstance(self.user_name, str) or self.user_name == "":
            raise ValueError("Invalid user_name")

        if not isinstance(self.first_name, str):
            raise ValueError("Invalid user first name")

        if not isinstance(self.last_name, str):
            raise ValueError(f"Invalid user last name: {self.last_name}")
