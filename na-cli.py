import logging
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
    menu = Menu()
    menu.show_menu()
