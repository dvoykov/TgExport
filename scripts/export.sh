#!/bin/bash
export PYTHONPATH=$(pwd)

# if the database exists and the DROP_DB_IF_EXISTS parameter is set to True, drop the database.
# Otherwise, stop the script execution.
DROP_DB_IF_EXISTS=True

# Init database
python db/init_db.py "$DROP_DB_IF_EXISTS"

# Telegram parameters
API_ID=""
API_HASH=""
CHAT_ID=
SESSION_NAME=""

# Save messages and users to pickle-files
SAVE_PICKLE=True

# If MSG_PKL_FILE and USR_PKL_FILE are non-empty, data will be loaded from these pickle files.
# Otherwise, the data is exported directly from Telegram.
MSG_PKL_FILE=""
USR_PKL_FILE=""

# export Telegram messages and store them in database
python src/export.py "$API_ID" "$API_HASH" "$CHAT_ID" "$SESSION_NAME" "$SAVE_PICKLE" "$MSG_PKL_FILE" "$USR_PKL_FILE"