import os

import client.data as data
import client.storage.controller as controller

from client.crypto import utils
from client.crypto.key_map import KeyMap

from client.crypto.exceptions import WrongPassword
from client.storage.exceptions import FullStorage

AES_CRYPTO = None


def has_signed_up():
    """
    Checks if a user already signed up
    :return: a boolean true regarding if the user already signed up
    """
    return data.data_file_exists(utils.KEY_MAP_FILE_NAME) and KeyMap.verify_content()


def sign_up(password):
    """
    Given a password, this method signs up a user by creating the cryptographic keys which it
    will use during the program
    :param password: password
    :return:
    """
    controller.create_keys(password)


def verify_password(password):
    """
    Verifies that this is a indeed the registered password
    :param password: password
    :return:
    """
    try:
        global AES_CRYPTO
        AES_CRYPTO = controller.verify_password(password)
    except WrongPassword as err:
        raise err


def setup():
    """
    Sets up all the stash folder of the client and initializes the server's storage
    :return:
    """
    controller.setup_stash()
    controller.setup_cloud(AES_CRYPTO)


def upload_file(path, filename):
    """
    Giuen a file path, uploads a file to the server's cloud
    :param path: a path to file name, a string
    :param filename: a file name, a string
    :return:
    """
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
    controller.upload_data(filename, AES_CRYPTO)


def download_file(path, filename):
    """
    Downloads a file
    :param path: a path for a file
    :param filename: a file name
    :return:
    """
    controller.download_file(filename, path, filename, AES_CRYPTO)


def delete_file(filename):
    """
    Deletes a file
    :param filename: a file name
    :return:
    """
    controller.delete_file(filename)
