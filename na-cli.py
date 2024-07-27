import logging
import os
from datetime import datetime
from network_analyzer import Menu


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    log_filename = os.path.join(
        "logs", datetime.now().strftime("%Y%m%d_%H%M%S_crash.log")
    )
    logger = setup_logger("main_logger", log_filename)

    try:
        raise ValueError("Hello")
        menu = Menu()
        menu.show_menu()
    except Exception as e:
        logger.error("An error occurred", exc_info=True)
        print(f"An error occurred. Check the log file {log_filename} for more details.")
