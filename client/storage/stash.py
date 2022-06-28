import client.data as data
import client.storage.utils as utils

import re

FILE_NAME = 'data%d.oram'


class Stash:
    """
    The Stash of the client
    """
    def __init__(self):
        if not data.is_folder(utils.STASH_FOLDER_NAME):
            data.create_folder(utils.STASH_FOLDER_NAME)

    def get_data_file_name(self, data_id):
        """
        Returns data file name given an ID
        :param data_id: an ID labeled to a data file
        :return: data file name
        """
        return FILE_NAME % data_id

    def get_data_block(self, data_id):
        """
        Returns a data block
        :param data_id: an ID labeled to a data block
        :return: data block
        """
        if data.is_data_file_in_stash(self.get_data_file_name(data_id)):
            with data.open_data_file_in_stash(self.get_data_file_name(data_id), 'rb') as data_block:
                return data_id, data_block.read()

    def get_potential_data_ids(self):
        """
        Returns potential data IDs which mean all the ids of real data files (not dummies)
        :return: potential data IDs which mean all the ids of real data files (not dummies)
        """
        data_ids = []
        stash_file_names = data.get_stash_data_file_names()
        for file_name in stash_file_names:
            data_ids.append(int(re.findall(r'\d+', file_name)[0]))
        return data_ids

    @property
    def size(self):
        """
        Property of the Stash - its size
        :return:
        """
        return data.get_stash_size()

    def add_file(self, data_id, token):
        """
        Adds file to the Stash
        :param data_id: data ID of a data file
        :param token: the data itself
        :return:
        """
        with data.open_data_file_in_stash(self.get_data_file_name(data_id), 'wb') as \
                data_file:
            data_file.write(token)

    def open_file(self, data_id):
        """
        Opens a file
        :param data_id: data ID of a data file
        :return: the data file (called interchangeably a data block)
        """
        with data.open_data_file_in_stash(self.get_data_file_name(data_id), 'rb') as \
                data_file:
            data_block = data_file.read()
            return data_block

    def delete_data_block(self, data_id):
        """
        Deletes a data block
        :param data_id: data ID of a data block
        :return:
        """
        data.delete_data_file_in_stash(self.get_data_file_name(data_id))

    def delete_data_blocks(self, data_ids):
        """
        Deletes data blocks
        :param data_ids: data IDs of data blocks
        :return:
        """
        for data_id in data_ids:
            self.delete_data_block(data_id)
