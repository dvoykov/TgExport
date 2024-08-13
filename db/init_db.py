import sqlite3
from sqlite3 import Error
import os
import sys
from loguru import logger

from config import db_params


def create_database(drop_if_exists: bool = False) -> int:
    """
    Creates a SQLite database based on the provided initialization script.

    Args:
        drop_if_exists (bool): If True, the existing database will be deleted before creation.
                               If False, the script will terminate if the database already exists.

    Returns:
        int: Status code where 0 indicates success,
             1 indicates the database already exists and was not dropped,
             2 indicates an error occurred while reading the initialization script,
             3 indicates an SQLite execution error,
             4 indicates a general execution error.
    """
    result = 0

    db_path = db_params["db_file"]
    init_script = db_params["init_script"]

    # Check if the database already exists
    if os.path.exists(db_path):
        if drop_if_exists:
            logger.warning(f"Database at {db_path} already exists. Deleting it now...")
            os.remove(db_path)
            logger.info(f"Database at {db_path} deleted.")
        else:
            print(f"Database at {db_path} already exists. Operation terminated.")
            return 1

    # Attempt to read the initialization script
    try:
        with open(init_script, "r") as file:
            sql_query = file.read()

    except (FileNotFoundError, IOError, Exception) as e:
        logger.exception(f"An error occurred: {str(e)}")
        return 2

    if result != 0:
        return result

    # Attempt to connect to the SQLite database
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    # Split the SQL script into individual statements
    sql_statements = sql_query.strip().split(";")

    # Execute each SQL statement
    for statement in sql_statements:
        if statement.strip():
            try:
                cursor.execute(statement)

                conn.commit()

            except Error as e:
                logger.error(f'The sqlite error "{e}" occurred.')
                conn.close()
                return 3
            except Exception as e:
                logger.exception(f'The error "{e}" occurred')
                conn.close()
                return 4

    if conn:
        conn.close()

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError(
            "Incorrect usage. Please provide all required arguments.\n"
            "Usage: python init_db.py <drop_db_if_exists>\n"
        )

    _, drop_db_if_exists = sys.argv

    result = create_database(bool(drop_db_if_exists))

    if result == 0:
        logger.info("The database was created successfully.")
