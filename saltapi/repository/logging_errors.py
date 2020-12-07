import logging


def setup_logging(name, log_file_name, log_file_format,  level: logging = logging.INFO):
    handler = logging.FileHandler(log_file_name)
    handler.setFormatter(log_file_format)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
