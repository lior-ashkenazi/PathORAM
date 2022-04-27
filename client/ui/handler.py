import os

import client.data as data
import client.storage.controller as controller

from client.crypto import utils
from client.crypto.key_map import KeyMap

from client.crypto.exceptions import WrongPassword
from client.storage.exceptions import FullStorage, DownloadFileError, FileSizeError

AES_CRYPTO = None


def has_signed_up():
    return data.data_file_exists(utils.KEY_MAP_FILE_NAME) and KeyMap.verify_content()


def sign_up(password):
    controller.create_keys(password)


def verify_password(password):
    try:
        global AES_CRYPTO
        AES_CRYPTO = controller.verify_password(password)
    except WrongPassword as err:
        raise err


def setup():
    controller.setup_stash()
    controller.setup_cloud(AES_CRYPTO)


def upload_file(path, filename):
    # file name should be only filename! no path
    try:
        with open(os.path.join(path, filename), 'rb') as file:
            file_input = file.read()
    except (FileExistsError, FileNotFoundError) as err:
        raise err

    free_storage_size = controller.get_max_storage_size() - controller.get_used_storage_size()
    if not controller.is_storage_available(len(file_input), free_storage_size):
        raise FullStorage("Storage is full")
    controller.save_file_input(filename, file_input, AES_CRYPTO)
    controller.update_data(filename, AES_CRYPTO)


def download_file(path, filename):
    controller.download_file(filename, path, filename, AES_CRYPTO)


def delete_file(filename):
    controller.delete_file(filename)
