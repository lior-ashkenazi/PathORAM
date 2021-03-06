import client.storage.utils as utils
import client.data as data

import json

JSON_FILES = 'files'
JSON_ID_COUNTER = 'counter'
JSON_FILE_NAME = 'data_file_name'
JSON_FILE_SIZE = 'file_size'
JSON_DATA_BLOCKS = 'data_blocks'


class DataFileMap:
    """
    A map for the data files in the stash/server
    """
    def __init__(self):
        if not data.data_file_exists(utils.FILE_MAP_FILE_NAME):
            with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.WRITE_MODE) as data_file_map:
                json.dump({JSON_FILES: (), JSON_ID_COUNTER: 0}, data_file_map,
                          indent=utils.JSON_INDENT)

    def add_data_file(self, data_file_name, file_size, data_blocks, data_id_counter):
        """
        Adds file to the map
        :param data_file_name: a data file name
        :param file_size: the data file's size
        :param data_blocks: the data ids for the data blocks for the given file
        :param data_id_counter: the counter counting the amount of data blocks used
        :return:
        """
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_WRITE_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            file_data[JSON_FILES].append({JSON_FILE_NAME: data_file_name, JSON_FILE_SIZE: file_size,
                                          JSON_DATA_BLOCKS: data_blocks})
            file_data[JSON_ID_COUNTER] = data_id_counter
            data_file_map.seek(utils.FILE_BEGIN)
            json.dump(file_data, data_file_map, indent=utils.JSON_INDENT, sort_keys=True)
            data_file_map.truncate()

    def get_data_files(self):
        """
        Returns all the names of the known files which were processed
        :return: all the names of the known files which were processed
        """
        file_names = list()
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            for file in file_data[JSON_FILES]:
                file_names.append(file[JSON_FILE_NAME])
            return file_names

    def get_id_counter(self):
        """
        Returns the counter of the data blocks
        :return: the counter of the data blocks
        """
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            return file_data[JSON_ID_COUNTER]

    def get_data_ids_of_file(self,data_file_name):
        """
        Returns a list of all the data blocks containing the given file
        :param data_file_name: a data file name
        :return: a list of all the data blocks containing the given file
        """
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            for file in file_data[JSON_FILES]:
                if file[JSON_FILE_NAME] == data_file_name:
                    return file[JSON_DATA_BLOCKS]

    def get_data_file_length(self, data_file_name):
        """
        Returns the size of the data file
        :param data_file_name: a data file name
        :return: the size of the data file
        """
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            for file in file_data[JSON_FILES]:
                if file[JSON_FILE_NAME] == data_file_name:
                    return file[JSON_FILE_SIZE]

    def delete_data_file(self, data_file_name):
        """
        Deletes a data file by deleting all its data blocks
        :param data_file_name: a data file name
        :return:
        """
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_WRITE_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            files = file_data[JSON_FILES]
            for entry in list(files):
                if entry[JSON_FILE_NAME] == data_file_name:
                    files.remove(entry)
                    break
            data_file_map.seek(utils.FILE_BEGIN)
            json.dump(file_data, data_file_map, indent=utils.JSON_INDENT, sort_keys=True)
            data_file_map.truncate()

