import os
import math

import client.config as config
import client.storage.utils as utils
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
    key_map = AESCryptography.create_keys(password)
    key_map.save_to_file()


def verify_password(password):
    key_map = KeyMap.load_from_file()
    return AESCryptography(key_map, password)


def setup_cloud(aes_crypto):
    PathORAM(aes_crypto).setup_cloud()


def setup_stash():
    Stash()


def get_uploaded_data_file_names():
    return DataFileMap().get_data_files()


def save_file_input(filename, file_input, aes_crypto):
    logger.info(f"START UPLOAD OF FILE {filename}")
    FileProcessor(aes_crypto).split(filename, file_input)


def update_data(file_name, aes_crypto):
    data_ids = DataFileMap().get_data_ids_of_file(file_name)
    data_entries = TreeMap().get_data_entries(data_ids)
    PathORAM(aes_crypto).update(data_entries)
    logger.info("END UPLOAD OF FILE")


def delete_file(file_name):
    data_ids = DataFileMap().get_data_ids_of_file(file_name)
    TreeMap().delete_data_ids(data_ids)
    Stash().delete_data_blocks(data_ids)
    DataFileMap().delete_data_file(file_name)
    logger.info("DELETE HAS BEEN SUCCESSFUL")


def save_file(joined_file, path, desired_file_name):
    with open(os.path.join(path, desired_file_name), 'wb') as file:
        file.write(joined_file)


def download_file(file_name, path, desired_file_name, aes_crypto):
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
    return PathORAM.get_max_oram_storage_size()


def get_used_storage_size():
    number_data_ids = TreeMap().count_data_ids()
    return number_data_ids * config.BLOCK_SIZE


def is_storage_available(needed_storage_size, free_storage_size):
    return (math.ceil(
        needed_storage_size / config.BLOCK_SIZE) * config.BLOCK_SIZE) <= free_storage_size
