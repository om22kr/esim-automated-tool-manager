import logging
from pathlib import Path


# ============================================================
# LOGGER CONFIGURATION
# ============================================================

LOGGER_NAME = "esim_tool_manager"


def get_log_directory():
    """
    Return the directory used for application logs.
    """

    log_directory = (
        Path(__file__).parent.parent
        / "logs"
    )

    log_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return log_directory


def get_log_file():
    """
    Return the application log file path.
    """

    return (
        get_log_directory()
        / "manager.log"
    )


# ============================================================
# GET LOGGER
# ============================================================

def get_logger():
    """
    Create and return the application logger.
    """

    logger = logging.getLogger(
        LOGGER_NAME
    )

    # Prevent duplicate handlers.
    if logger.handlers:
        return logger

    logger.setLevel(
        logging.INFO
    )

    logger.propagate = False

    log_file = get_log_file()

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    return logger


# ============================================================
# INFORMATION LOG
# ============================================================

def log_info(message):
    """
    Record an informational message.
    """

    logger = get_logger()

    logger.info(
        str(message)
    )


# ============================================================
# WARNING LOG
# ============================================================

def log_warning(message):
    """
    Record a warning message.
    """

    logger = get_logger()

    logger.warning(
        str(message)
    )


# ============================================================
# ERROR LOG
# ============================================================

def log_error(message):
    """
    Record an error message.
    """

    logger = get_logger()

    logger.error(
        str(message)
    )


# ============================================================
# DEBUG LOG
# ============================================================

def log_debug(message):
    """
    Record a debug message.

    Debug messages are not normally shown because
    the application logger uses INFO level.
    """

    logger = get_logger()

    logger.debug(
        str(message)
    )


# ============================================================
# CLEAR LOG
# ============================================================

def clear_logs():
    """
    Clear the current log file.
    """

    log_file = get_log_file()

    try:

        # Remove handlers temporarily so the
        # Windows file can be safely rewritten.

        logger = logging.getLogger(
            LOGGER_NAME
        )

        handlers = list(
            logger.handlers
        )

        for handler in handlers:
            handler.close()
            logger.removeHandler(
                handler
            )

        with open(
            log_file,
            "w",
            encoding="utf-8"
        ):
            pass

        # Recreate logger handler.
        get_logger()

        return True, (
            "Log file cleared successfully."
        )

    except Exception as error:

        return False, (
            f"Could not clear log file: "
            f"{error}"
        )


# ============================================================
# READ LOGS
# ============================================================

def read_logs():
    """
    Read and return the complete log file.
    """

    log_file = get_log_file()

    if not log_file.exists():
        return ""

    try:

        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except Exception as error:

        return (
            f"Unable to read log file: "
            f"{error}"
        )