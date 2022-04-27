# TODO might delete this class and loggers

import logging

import client.data as data


def get_logger(name):
    logger = logging.getLogger(name)
    # from official documentation: "logging messages which have severity level or higher *will be
    # emitted* by whichever handler of handlers service this logger..."
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(data.get_log_data_file_name())
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(message)s")

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger
