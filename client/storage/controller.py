import os
import math

import client.config as config
import client.log as log
from client.storage.file_processor import FileProcessor
from client.storage.data_file_map import DataFileMap
from client.storage.tree_map import TreeMap
from client.storage.oram import PathORAM
from client.storage.stash import Stash
from client.crypto.aes_crypto import AESCryptography
from client.crypto.key_map import KeyMap
from client.storage.exceptions import DownloadFileError, FileNotInStorage

logger = log.get_logger(__name__)


def create_keys(password):
    """
    Generates cryptographic keys given a password
    :param password: a password
    :return:
    """
    key_map = AESCryptography.create_keys(password)
    key_map.save_to_file()


def verify_password(password):
    """
    Verifies that the given password is the password the user sign-up with
    :param password: a password
    :return:
    """
    key_map = KeyMap.load_from_file()
    return AESCryptography(key_map, password)


def setup_cloud(aes_crypto):
    """
    Sets up the server's cloud with the required generated null data blocks
    :param aes_crypto: a cryptographic object for encrypting and decrypting data blocks
    :return:
    """
    PathORAM(aes_crypto).setup_cloud()


def setup_stash():
    """
    Sets up stash
    :return:
    """
    Stash()


def save_file_input(filename, file_input, aes_crypto):
    """
    Converting a file into data files
    :param filename:a file name
    :param file_input: the file's data
    :param aes_crypto: a cryptographic object for encrypting and decrypting data blocks
    :return:
    """
    logger.info(f"START UPLOAD OF FILE {filename}")
    FileProcessor(aes_crypto).split(filename, file_input)


def upload_data(file_name, aes_crypto):
    """
    Uploads a file, in its data files form to the server
    :param file_name: a file name
    :param aes_crypto: a cryptographic object for encrypting and decrypting data blocks
    :return:
    """
    data_ids = DataFileMap().get_data_ids_of_file(file_name)
    data_entries = TreeMap().get_data_entries(data_ids)
    PathORAM(aes_crypto).upload(data_entries)
    logger.info("END UPLOAD OF FILE")


def delete_file(file_name):
    """
    Deletes a file from the program's eco-system
    :param file_name: a file name
    :return:
    """
    data_ids = DataFileMap().get_data_ids_of_file(file_name)
    TreeMap().delete_data_ids(data_ids)
    Stash().delete_data_blocks(data_ids)
    DataFileMap().delete_data_file(file_name)
    logger.info("DELETE HAS BEEN SUCCESSFUL")


def save_file(joined_file, path, desired_file_name):
    """
    Saves a file
    :param joined_file: a joined file, meaning it was joined from data blocks
    :param path: a path for a file
    :param desired_file_name: a file name to save unto the disk
    :return:
    """
    with open(os.path.join(path, desired_file_name), 'wb') as file:
        file.write(joined_file)


def download_file(file_name, path, desired_file_name, aes_crypto):
    """
    Downloads a file from the server
    :param file_name: a file name
    :param path: a path for a file
    :param desired_file_name: the desired file label we want to save with
    :param aes_crypto: a cryptographic object for encrypting and decrypting data blocks
    :return:
    """
    logger.info(f"START DOWNLOAD OF {file_name} as {desired_file_name}")
    data_ids = DataFileMap().get_data_ids_of_file(file_name)
    if data_ids is None:
        raise FileNotInStorage("File is not in storage.")
    downloaded_data_blocks = PathORAM(aes_crypto).download(data_ids)

    if len(data_ids) != len(downloaded_data_blocks):
        raise DownloadFileError("An error occurred during file download.")

    joined_file = FileProcessor().join(downloaded_data_blocks,
                                       DataFileMap().get_data_file_length(file_name))
    save_file(joined_file, path, desired_file_name)
    logger.info(f"END DOWNLOAD OF FILE {file_name}")


def get_max_storage_size():
    """
    Returns the max capacity of the stash
    :return: the max capacity of the stash
    """
    return PathORAM.get_max_oram_storage_size()


def get_used_storage_size():
    """
    Returns the used storage size
    :return: the used storage size
    """
    number_data_ids = TreeMap().count_data_ids()
    return number_data_ids * config.BLOCK_SIZE


def is_storage_available(needed_storage_size, free_storage_size):
    """
    Checks if there is still available space in the stash
    :param needed_storage_size: the needed storage size
    :param free_storage_size: the amount of free size we have for storing more data
    :return: a True/False answer regarding if there is still available space in the stash
    """
    return (math.ceil(
        needed_storage_size / config.BLOCK_SIZE) * config.BLOCK_SIZE) <= free_storage_size
