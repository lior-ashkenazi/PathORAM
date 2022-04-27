import os
from client.storage import utils

BASE_DIR = os.path.dirname(__file__)
STASH_DIR = os.path.join(BASE_DIR, utils.STASH_FOLDER_NAME)


def is_folder(folder_name):
    return os.path.isdir(os.path.join(BASE_DIR, folder_name))


def create_folder(folder_name):
    os.makedirs(os.path.join(BASE_DIR, folder_name))


def open_data_file(filename, mode):
    return open(os.path.join(BASE_DIR, filename), mode)


def get_stash_size():
    return len([name for name in os.listdir(STASH_DIR) if
                os.path.isfile(os.path.join(STASH_DIR, name))])


def open_data_file_in_stash(filename, mode):
    return open(os.path.join(STASH_DIR, filename), mode)


def is_data_file_in_stash(filename):
    return os.path.isfile(os.path.join(STASH_DIR, filename))


def delete_data_file_in_stash(filename):
    if os.path.isfile(os.path.join(STASH_DIR, filename)):
        os.remove(os.path.join(STASH_DIR, filename))


def get_stash_data_file_names():
    return os.listdir(STASH_DIR)


def data_file_exists(filename):
    return os.path.isfile(os.path.join(BASE_DIR, filename))


def get_log_data_file_name():
    return os.path.join(BASE_DIR, utils.LOG_FILE_NAME)
