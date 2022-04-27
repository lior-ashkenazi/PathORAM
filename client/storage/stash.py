import client.data as data
import client.storage.utils as utils

import re

FILE_NAME = 'data%d.oram'


class Stash:
    def __init__(self):
        if not data.is_folder(utils.STASH_FOLDER_NAME):
            data.create_folder(utils.STASH_FOLDER_NAME)

    def get_data_file_name(self, data_id):
        return FILE_NAME % data_id

    def get_data_block(self, data_id):
        if data.is_data_file_in_stash(self.get_data_file_name(data_id)):
            with data.open_data_file_in_stash(self.get_data_file_name(data_id), 'rb') as data_block:
                return data_id, data_block.read()

    def get_potential_data_ids(self):
        data_ids = []
        stash_file_names = data.get_stash_data_file_names()
        for file_name in stash_file_names:
            data_ids.append(int(re.findall(r'\d+', file_name)[0]))
        return data_ids

    @property
    def size(self):
        return data.get_stash_size()

    def add_file(self, data_id, token):
        with data.open_data_file_in_stash(self.get_data_file_name(data_id), 'wb') as \
                data_file:
            data_file.write(token)

    def open_file(self, data_id):
        with data.open_data_file_in_stash(self.get_data_file_name(data_id), 'rb') as \
                data_file:
            data_block = data_file.read()
            return data_block

    def delete_data_block(self, data_id):
        data.delete_data_file_in_stash(self.get_data_file_name(data_id))

    def delete_data_blocks(self, data_ids):
        for data_id in data_ids:
            self.delete_data_block(data_id)
