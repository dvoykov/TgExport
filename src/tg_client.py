from typing import List, Tuple
from datetime import datetime
import pickle
import sys
import os

from loguru import logger
from dateutil import tz

from telethon import TelegramClient
from telethon.tl.types import PeerUser
from telethon.errors import ApiIdInvalidError

from models import Msg, MsgReaction, User


class TgClient:
    """
    A client to interact with Telegram using Telethon library.

    Attributes:
        api_id (str): The API ID for Telegram.
        api_hash (str): The API hash for Telegram.
        session_name (str): The name of the session.
    """

    def __init__(self, api_id: str, api_hash: str, session_name: str):
        """
        Initializes the TgClient with API ID, API hash, and session name.

        Args:
            api_id (str): The API ID for Telegram.
            api_hash (str): The API hash for Telegram.
            session_name (str): The name of the session.
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.session = None

    async def connect(self):
        """
        Connects to the Telegram session.

        Returns:
            Tuple[int, str]:
                A tuple containing a status code and a message.
                    0 and "OK" if connection is successful,
                    1 and an error message if API ID or hash is invalid,
                    2 and an error message for any other exception.
        """
        try:
            self.session = TelegramClient(self.session_name, self.api_id, self.api_hash)

            if not self.session.is_connected():
                await self.session.connect()

            if not await self.session.is_user_authorized():
                await self.session.start()

            return 0, "OK"
        except ApiIdInvalidError:
            return 1, "The api_id/api_hash combination is invalid"
        except Exception as e:
            return 2, e.args[0]

    async def disconnect(self):
        """Disconnects from the Telegram session."""
        if self.session.is_connected():
            await self.session.disconnect()

    async def export_messages(
        self,
        chat_id: int,
        start_date: datetime = None,
        end_date: datetime = None,
        save_pkl: bool = False,
    ) -> Tuple[int, List[Msg], List[User]]:
        """
        Exports messages from a Telegram chat.

        Args:
            chat_id (int): The ID of the chat to export messages from.
            start_date (datetime, optional): The start date for message export. Defaults to None.
            end_date (datetime, optional): The end date for message export. Defaults to None.
            save_pkl (bool, optional): Whether to save the messages to a pickle file. Defaults to False.

        Returns:
        """
        messages = []
        users_set = set([])
        users = []

        if not self.session.is_connected():
            return 1, messages, users

        min_id = 0
        first_message = []

        if start_date:
            pre_first_msg = await self.session.get_messages(
                chat_id, offset_date=start_date, limit=1
            )

            first_msg = await self.session.get_messages(
                chat_id, min_id=pre_first_msg[0].id, limit=1, reverse=True
            )

            min_id = first_msg[0].id
            first_message = [first_msg[0]]

        max_id = 0
        last_message = []

        if end_date:
            last_msg = await self.session.get_messages(
                chat_id, offset_date=end_date, limit=1
            )

            max_id = last_msg[0].id
            last_message = [last_msg[0]]

        raw_messages = (
            await self.session.get_messages(chat_id, min_id=min_id, max_id=max_id)
            + first_message
            + last_message
        )

        for msg in raw_messages:
            if msg and msg.id and msg.text and msg.date:
                users_set.add(msg.from_id.user_id)

                reply_to_msg_id = (
                    None if msg.reply_to is None else msg.reply_to.reply_to_msg_id
                )

                reactions = []

                if msg.reactions and msg.reactions.recent_reactions:
                    for reaction in msg.reactions.recent_reactions:
                        users_set.add(reaction.peer_id.user_id)

                        mr = MsgReaction(
                            chat_id=chat_id,
                            msg_id=msg.id,
                            user_id=reaction.peer_id.user_id,
                            dt=reaction.date.astimezone(tz.tzlocal()),
                            emoticon=reaction.reaction.emoticon,
                        )
                        reactions.append(mr)

                message = Msg(
                    chat_id,
                    msg.from_id.user_id,
                    msg.id,
                    msg.text,
                    msg.date.astimezone(tz.tzlocal()),
                    reply_to_msg_id,
                    reactions,
                )
                messages.append(message)

        for user_id in users_set:
            try:
                user_entity = await self.session.get_entity(PeerUser(user_id))

                first_name = user_entity.first_name if user_entity.first_name else ""
                last_name = user_entity.last_name if user_entity.last_name else ""

                user = User(
                    chat_id=chat_id,
                    user_id=user_id,
                    user_name=user_entity.username,
                    first_name=first_name,
                    last_name=last_name,
                )

                users.append(user)
            except ValueError:
                pass

        if save_pkl:
            messages_pkl_file = f'{self.session_name}_messages_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.pkl'
            users_pkl_file = f'{self.session_name}_users_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.pkl'

            pkl_dir = os.path.join(os.path.dirname(sys.path[0]), "pkl")
            pkl_messages_path = os.path.join(pkl_dir, messages_pkl_file)
            pkl_users_path = os.path.join(pkl_dir, users_pkl_file)

            os.makedirs(pkl_dir, exist_ok=True)

            with open(pkl_messages_path, "wb") as f:
                pickle.dump(messages, f)

            with open(pkl_users_path, "wb") as f:
                pickle.dump(messages, f)

            logger.info(f"File `{messages_pkl_file}` saved successfully.")
            logger.info(f"File `{users_pkl_file}` saved successfully.")

        return 0, messages, users
