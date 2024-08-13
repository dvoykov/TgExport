from typing import Tuple, List
from datetime import datetime
import sys
import asyncio
import pickle
from loguru import logger

from src.tg_client import TgClient
from src.models import Msg
from db.controller import MsgController


async def export(
    client: TgClient,
    chat_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    save_pkl: bool = True,
) -> Tuple[List[Msg]]:
    """
    Exports messages from a specified Telegram chat using the provided TgClient.

    Args:
        client (TgClient): An instance of TgClient to interact with the Telegram API.
        chat_id (int): The ID of the chat from which to export messages.
        start_date (datetime, optional): The start date for message export. Defaults to None.
        end_date (datetime, optional): The end date for message export. Defaults to None.

    Returns:
        Tuple[int, List[Msg]]:
            A tuple containing a status code and a list of messages.
                0 and the list of messages if successful,
                otherwise an error code and an empty list.
    """
    logger.info("Export of Telegram messages started ...")

    x = 0
    messages = []
    users = []

    try:
        await client.connect()

        x, messages, users = await client.export_messages(
            chat_id, start_date, end_date, save_pkl=save_pkl
        )

        if x == 0:
            logger.info(f"Export finished, total messages: {len(messages)}")
        else:
            logger.error(f"Export finished with errors. Error code: {x}")
    except Exception as e:
        logger.exception(f"Exception during `export_messages`: {e}")
    finally:
        await client.disconnect()

    return x, messages, users


if __name__ == "__main__":
    if len(sys.argv) < 8:
        raise RuntimeError(
            "Incorrect usage. Please provide all required arguments.\n"
            "Usage: python export.py <api_id> <api_hash> <chat_id> <session_name> <save_pickle> <msg_pickle_file> <usr_pickle_file>\n"
        )

    (
        _,
        api_id,
        api_hash,
        chat_id,
        session_name,
        save_pickle,
        msg_pickle_file,
        usr_pickle_file,
    ) = sys.argv

    if msg_pickle_file and usr_pickle_file:
        ### use already exported messages/users
        result = 0

        with open(msg_pickle_file, "rb") as file:
            messages = pickle.load(file)

        with open(usr_pickle_file, "rb") as file:
            users = pickle.load(file)
    else:
        ### export messages
        tg_client = TgClient(api_id, api_hash, session_name)

        result, messages, users = asyncio.run(
            export(client=tg_client, chat_id=int(chat_id), save_pkl=bool(save_pickle))
        )

    ## save messages
    if result == 0:
        logger.info("Saving messages to the database ...")

        controller = MsgController()

        status_code, status_message = controller.save_data(messages, users)

        if status_code == 0:
            logger.info(status_message)
