import logging  # Logging server operation / streaming to stdout
import datetime  # used for appending exact date / start time to log filenames


# Set up our main logging handler which will "forward" log messages to file_logger and console_logger for processing.
def log_setup():
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    log_format = logging.Formatter(f'{datetime.datetime.now()}/%(levelname)s/%(threadName)s: %(message)s')  # Setup our log message format

    file_logger = logging.FileHandler(f'logs/log-{datetime.datetime.now()}', mode='w', encoding='utf-8')  # Setup file logging to text files
    file_logger.setLevel(logging.DEBUG)
    file_logger.setFormatter(log_format)
    logger.addHandler(file_logger)

    console_logger = logging.StreamHandler()  # Setup logging output to stdout (screen)
    console_logger.setLevel(logging.DEBUG)
    console_logger.setFormatter(log_format)
    logger.addHandler(console_logger)

    return logger
