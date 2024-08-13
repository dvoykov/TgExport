from typing import Callable, Tuple
from threading import Thread
from datetime import datetime, timedelta
import time
import asyncio
from tqdm.asyncio import tqdm as async_tqdm
from tqdm import tqdm


def show_progress(func: Callable, descr: str) -> Tuple[int, str]:
    """
    Displays a progress bar while executing the given function in a separate thread.
    Returns a tuple indicating the result status and any error message.

    Parameters:
        func (Callable): The function to be executed.
        descr (str): The description to be displayed on the progress bar.

    Returns:
        Tuple[int, str]:
            A tuple where the first element is the result status (0 for success, 1 for failure),
            and the second element is an error message if an exception occurred,
            otherwise an empty string.

    The progress bar will run and update periodically to show the progress of the task.

    Example of usage:
        def dummy_task() -> None:
            time.sleep(5)

        result, error = show_progress(dummy_task, "Processing")
        print(f"Result: {result}, Error: {error}")
    """
    result = 0
    err_msg = ""
    progress_bar = async_tqdm(desc=descr, unit=" step")

    thread = Thread(target=func)
    thread.start()

    try:
        while thread.is_alive():
            progress_bar.update(1)
            time.sleep(0.1)
    except Exception as e:
        result = 1
        err_msg = str(e)
    finally:
        progress_bar.close()
        thread.join()

    return result, err_msg


async def async_show_progress(func: Callable[[], None], descr: str) -> Tuple[int, str]:
    """
    Displays a progress bar while executing the given asynchronous function.
    Returns a tuple indicating the result status and any error message.

    Parameters:
        func (Callable): The asynchronous function to be executed.
        descr (str): The description to be displayed on the progress bar.

    Returns:
        Tuple[int, str]:
            A tuple where the first element is the result status (0 for success, 1 for failure),
            and the second element is an error message if an exception occurred,
            otherwise an empty string.

    The progress bar will run and update periodically to show the progress of the task.

    Example of usage:
        async def dummy_task() -> None:
            await asyncio.sleep(5)

        result, error = await show_progress(dummy_task, "Processing")
        print(f"Result: {result}, Error: {error}")
    """
    result = 0
    err_msg = ""
    progress_bar = tqdm(desc=descr, unit=" step")

    async def run_with_progress():
        nonlocal result, err_msg
        try:
            task = asyncio.create_task(func())
            while not task.done():
                progress_bar.update(1)
                await asyncio.sleep(0.1)
            await task
        except Exception as e:
            result = 1
            err_msg = str(e)
        finally:
            progress_bar.close()

    await run_with_progress()

    return result, err_msg


def get_last_two_days() -> Tuple[datetime, datetime, datetime, datetime]:
    """
    Calculate the start and end timestamps of the last two days.

    This function calculates and returns the start and end timestamps for the
    day before yesterday and yesterday.

    Returns:
        Tuple[datetime, datetime, datetime, datetime]: A tuple containing:
            - The start of the day before yesterday.
            - The end of the day before yesterday.
            - The start of yesterday.
            - The end of yesterday.
    """

    now = datetime.now()
    start_of_today = datetime(now.year, now.month, now.day)

    start_of_yesterday = start_of_today - timedelta(days=1)
    start_of_before_yesterday = start_of_yesterday - timedelta(days=1)

    end_of_yesterday = start_of_today - timedelta(seconds=1)
    end_of_before_yesterday = start_of_yesterday - timedelta(seconds=1)

    return (
        start_of_before_yesterday,
        end_of_before_yesterday,
        start_of_yesterday,
        end_of_yesterday,
    )
