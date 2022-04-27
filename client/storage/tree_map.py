import client.storage.utils as utils
import client.data as data
import client.config as config

import json

JSON_LEAF_ID = 'leaf_id'
JSON_DATA_ID = 'data_id'


class TreeMap:
    def __init__(self):
        if not data.data_file_exists(utils.TREE_MAP_FILE_NAME):
            with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.WRITE_MODE) as loc_map:
                json.dump((), loc_map, indent=utils.JSON_INDENT)

    def add_data(self, data_id):
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_WRITE_MODE) as loc_map:
            loc_data = json.load(loc_map)
            # minus config means not in server, without a minus - is in server
            loc_data.append({JSON_LEAF_ID: -config.get_random_leaf_id(), JSON_DATA_ID: data_id})
            loc_map.seek(0)
            json.dump(loc_data, loc_map, indent=utils.JSON_INDENT, sort_keys=True)
            loc_map.truncate()

    def delete_data_ids(self, data_ids):
        data_ids_copy = list(data_ids)
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_WRITE_MODE) as loc_map:
            loc_data = json.load(loc_map)
            for data_entry in list(loc_data):
                if data_entry[JSON_DATA_ID] in data_ids:
                    loc_data.remove(data_entry)
                    data_ids_copy.remove(data_entry[JSON_DATA_ID])
                if not data_ids_copy:
                    break
            loc_map.seek(0)
            json.dump(loc_data, loc_map, indent=utils.JSON_INDENT, sort_keys=True)
            loc_map.truncate()

    def get_data_entries(self, data_ids):
        data_ids_copy = list(data_ids)
        leaf_ids = list()
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_MODE) as loc_map:
            loc_data = json.load(loc_map)
            for data_entry in list(loc_data):
                if data_entry[JSON_DATA_ID] in data_ids:
                    leaf_ids.append((data_entry[JSON_DATA_ID], data_entry[JSON_LEAF_ID]))
                    data_ids_copy.remove(data_entry[JSON_DATA_ID])
                if not data_ids_copy:
                    break
        # Note that we return list of tuples!
        return leaf_ids

    def get_leaf_id(self, data_id):
        return self.get_data_entries([data_id])[0][1]

    def update_leaf_id(self, data_id, is_uploaded):
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_WRITE_MODE) as loc_map:
            loc_data = json.load(loc_map)
            for data_entry in loc_data:
                if data_entry[JSON_DATA_ID] == data_id:
                    if is_uploaded:
                        data_entry[JSON_LEAF_ID] = abs(data_entry[JSON_LEAF_ID])
                    else:
                        data_entry[JSON_LEAF_ID] = -data_entry[JSON_LEAF_ID]
                    break
            loc_map.seek(0)
            json.dump(loc_data, loc_map, indent=utils.JSON_INDENT, sort_keys=True)
            loc_map.truncate()

    def choose_fresh_leaf_id(self, data_id):
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_WRITE_MODE) as loc_map:
            loc_data = json.load(loc_map)
            for data_entry in loc_data:
                if data_entry[JSON_DATA_ID] == data_id:
                    data_entry[JSON_LEAF_ID] = -config.get_random_leaf_id()
                    break
            loc_map.seek(0)
            json.dump(loc_data, loc_map, indent=utils.JSON_INDENT, sort_keys=True)
            loc_map.truncate()

    def data_id_exist(self, data_id):
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_MODE) as loc_map:
            loc_data = json.load(loc_map)
            for data_entry in loc_data:
                if data_entry[JSON_DATA_ID] == data_id:
                    return True
            return False

    def count_data_ids(self):
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_MODE) as loc_map:
            return len(json.load(loc_map))
