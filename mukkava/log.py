'''
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
This module sets up logging chains, while this required for sys_logger, it is not for chat logger, however I have adopted the same methodology
simply to make understanding the code easier, rather then switching to the method use to setup a direct logger.

TODO: incorporate into logging section of config.toml
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''

import logging  # Logging server operation / streaming to stdout
import datetime  # used for appending exact date / start time to log filenames


# Set up our main logging handlers which will "forward" log messages to file_logger, console_logger and chat_file_logger for processing.
def log_setup(file, screen, chat):
    sys_logger = logging.getLogger('sys_logger')
    sys_logger.setLevel(logging.DEBUG)

    chat_logger = logging.getLogger('chat_logger')
    chat_logger.setLevel(logging.INFO)

    log_format = logging.Formatter(f'{datetime.datetime.now()}/%(levelname)s/%(threadName)s: %(message)s')  # Setup our log message format

    if file:  # if file is true, we need to log debug messages to a file
        file_logger = logging.FileHandler(f'configuration/sys-log/log-{datetime.datetime.now()}', mode='w', encoding='utf-8')  # Setup file logging to sys text files
        file_logger.setLevel(logging.DEBUG)
        file_logger.setFormatter(log_format)
        sys_logger.addHandler(file_logger)

    if screen:  # if screen is true, we need to log debug messages to stdout (terminal)
        console_logger = logging.StreamHandler()  # Setup logging output to stdout (screen)
        console_logger.setLevel(logging.DEBUG)
        console_logger.setFormatter(log_format)
        sys_logger.addHandler(console_logger)

    if chat:  # if chat is true, we need to log chat messages to a file
        chat_file_logger = logging.FileHandler(f'configuration/chat-log/log-{datetime.datetime.now()}', mode='w', encoding='utf-8')  # Setup file logging to chat text files
        chat_file_logger.setLevel(logging.INFO)
        chat_file_logger.setFormatter(log_format)
        chat_logger.addHandler(chat_file_logger)
        return sys_logger, chat_logger

    return sys_logger
