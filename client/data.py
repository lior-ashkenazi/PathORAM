import os
from client.storage import utils

# The program directory path
BASE_DIR = os.path.dirname(__file__)

# The stash directory path
STASH_DIR = os.path.join(BASE_DIR, utils.STASH_FOLDER_NAME)


def is_folder(folder_name):
    """
    Checks if a folder path contains a folder
    :param folder_name: a folder name
    :return: True/False
    """
    return os.path.isdir(os.path.join(BASE_DIR, folder_name))


def create_folder(folder_name):
    """
    Creates a folder given a folder name
    :param folder_name: a folder name
    :return:
    """
    os.makedirs(os.path.join(BASE_DIR, folder_name))


def open_data_file(filename, mode):
    """
    Opens a data file
    :param filename: a data file name
    :param mode: the mode with which we read the data file
    :return:
    """
    return open(os.path.join(BASE_DIR, filename), mode)


def get_stash_size():
    """
    Returns the stash's size
    :return: the stash's size
    """
    return len([name for name in os.listdir(STASH_DIR) if
                os.path.isfile(os.path.join(STASH_DIR, name))])


def open_data_file_in_stash(filename, mode):
    """
    Opens a data file in the stash
    :param filename: a data file name
    :param mode: the mode with which we read the data file
    :return:
    """
    return open(os.path.join(STASH_DIR, filename), mode)


def is_data_file_in_stash(filename):
    """
    Checks if a data file is in the stash
    :param filename: a data file name
    :return: True/False
    """
    return os.path.isfile(os.path.join(STASH_DIR, filename))


def delete_data_file_in_stash(filename):
    """
    Deletes a data file in the stash
    :param filename: a data file name
    :return:
    """
    if os.path.isfile(os.path.join(STASH_DIR, filename)):
        os.remove(os.path.join(STASH_DIR, filename))


def get_stash_data_file_names():
    """
    Returns the names of all the data files in the stash
    :return: the names of all the data files in the stash
    """
    return os.listdir(STASH_DIR)


def data_file_exists(filename):
    """
    Checks if a data file exists
    :param filename: a data file name
    :return:
    """
    return os.path.isfile(os.path.join(BASE_DIR, filename))


def get_log_data_file_name():
    """
    Returns the log file (used for setting the logger)
    :return: the log file (used for setting the logger)

    """
    return os.path.join(BASE_DIR, utils.LOG_FILE_NAME)
