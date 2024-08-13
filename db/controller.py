from typing import List, Tuple
from tqdm import tqdm
from loguru import logger

from config import db_params
from src.models import Msg, MsgReaction, User
from db.sqlite_connector import SQLiteConnector


class MsgController:
    def __init__(self):
        self.conn = SQLiteConnector(db_params["db_file"])
        status_code, status_message = self.conn.connect()

        if status_code != 0:
            raise RuntimeError(status_message)

    def save_data(self, messages: List[Msg], users: List[User]) -> Tuple[int, str]:
        msg_qty = len(messages)
        reactions_qty = sum([len(msg.reactions) for msg in messages])
        users_qty = len(users)

        for msg in tqdm(messages, "Saving messages"):
            status_code, status_message = self._save_single_message(msg)

            if status_code == 0:
                for reaction in msg.reactions:
                    status_code, status_message = self._save_single_reaction(reaction)

                    if status_code != 0:
                        logger.error(f"Error during reaction saving: {status_message}")
                        logger.error(f"Reaction data: {reaction}")
                        return status_code, status_message

            else:
                logger.error(f"Error during message saving: {status_message}")
                logger.error(f"Message data: {msg}")
                return status_code, status_message

        for user in tqdm(users, "Saving users"):
            status_code, status_message = self._save_single_user(user)

            if status_code != 0:
                logger.error(f"Error during user saving: {status_message}")
                logger.error(f"User data: {user}")
                return status_code, status_message

        return (
            0,
            f"Successfully saved in database {msg_qty} messages, {reactions_qty} reactions and {users_qty} users.",
        )

    def _save_single_message(self, msg: Msg) -> Tuple[int, str]:
        query = """
            insert or replace into messages (chat_id, user_id, msg_id, msg_text, msg_dt, reply_to_msg_id)
            values(?, ?, ?, ?, ?, ?)
        """

        params = (
            msg.chat_id,
            msg.user_id,
            msg.msg_id,
            msg.msg_text,
            msg.msg_dt,
            msg.reply_to_msg_id,
        )

        status_code, status_message = self.conn.execute_query(query, params)

        return status_code, status_message

    def _save_single_reaction(self, mr: MsgReaction) -> Tuple[int, str]:
        query = """
            insert or replace into reactions (chat_id, msg_id, user_id, emoticon)
            values(?, ?, ?, ?)
        """

        params = (
            mr.chat_id,
            mr.msg_id,
            mr.user_id,
            mr.emoticon,
        )

        status_code, status_message = self.conn.execute_query(query, params)

        return status_code, status_message

    def _save_single_user(self, u: User) -> Tuple[int, str]:
        query = """
            insert or replace into users (chat_id, user_id, user_name, first_name, last_name)
            values(?, ?, ?, ?, ?)
        """

        params = (
            u.chat_id,
            u.user_id,
            u.user_name,
            u.first_name,
            u.last_name,
        )

        status_code, status_message = self.conn.execute_query(query, params)

        return status_code, status_message
