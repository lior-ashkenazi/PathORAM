import client.storage.utils as utils
import client.data as data

import json

JSON_FILES = 'files'
JSON_ID_COUNTER = 'counter'
JSON_FILE_NAME = 'data_file_name'
JSON_FILE_SIZE = 'file_size'
JSON_DATA_BLOCKS = 'data_blocks'


class DataFileMap:
    def __init__(self):
        if not data.data_file_exists(utils.FILE_MAP_FILE_NAME):
            with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.WRITE_MODE) as data_file_map:
                json.dump({JSON_FILES: (), JSON_ID_COUNTER: 0}, data_file_map,
                          indent=utils.JSON_INDENT)

    def add_data_file(self, data_file_name, file_size, data_blocks, data_id_counter):
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_WRITE_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            file_data[JSON_FILES].append({JSON_FILE_NAME: data_file_name, JSON_FILE_SIZE: file_size,
                                          JSON_DATA_BLOCKS: data_blocks})
            file_data[JSON_ID_COUNTER] = data_id_counter
            data_file_map.seek(utils.FILE_BEGIN)
            json.dump(file_data, data_file_map, indent=utils.JSON_INDENT, sort_keys=True)
            data_file_map.truncate()

    def get_data_files(self):
        file_names = list()
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            for file in file_data[JSON_FILES]:
                file_names.append(file[JSON_FILE_NAME])
            return file_names

    def get_id_counter(self):
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            return file_data[JSON_ID_COUNTER]

    def get_data_ids_of_file(self,data_file_name):
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            for file in file_data[JSON_FILES]:
                if file[JSON_FILE_NAME] == data_file_name:
                    return file[JSON_DATA_BLOCKS]

    def get_data_file_length(self, data_file_name):
        with data.open_data_file(utils.FILE_MAP_FILE_NAME, utils.READ_MODE) as data_file_map:
            file_data = json.load(data_file_map)
            for file in file_data[JSON_FILES]:
                if file[JSON_FILE_NAME] == data_file_name:
                    return file[JSON_FILE_SIZE]

    def delete_data_file(self, data_file_name):
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

