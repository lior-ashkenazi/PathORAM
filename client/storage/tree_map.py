import client.storage.utils as utils
import client.data as data
import client.config as config

import json

JSON_LEAF_ID = 'leaf_id'
JSON_DATA_ID = 'data_id'


class TreeMap:
    """
    The map of the PathORAM Tree
    """
    def __init__(self):
        if not data.data_file_exists(utils.TREE_MAP_FILE_NAME):
            with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.WRITE_MODE) as loc_map:
                json.dump((), loc_map, indent=utils.JSON_INDENT)

    def add_data(self, data_id):
        """
        Adds a new mapping of a data block to a leaf
        :param data_id: a data ID of a data file
        :return:
        """
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_WRITE_MODE) as loc_map:
            loc_data = json.load(loc_map)
            # minus config means not in server, without a minus - is in server
            loc_data.append({JSON_LEAF_ID: -config.get_random_leaf_id(), JSON_DATA_ID: data_id})
            loc_map.seek(0)
            json.dump(loc_data, loc_map, indent=utils.JSON_INDENT, sort_keys=True)
            loc_map.truncate()

    def delete_data_ids(self, data_ids):
        """
        Deletes the data IDs from the map
        :param data_ids: data IDs
        :return:
        """
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
        """
        Returns the mapping of data IDs unto leaves
        :param data_ids: data IDs
        :return: tuples of (data_ID, leaf_ID)
        """
        data_ids_copy = list(data_ids)
        data_entries = list()
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_MODE) as loc_map:
            loc_data = json.load(loc_map)
            for data_entry in list(loc_data):
                if data_entry[JSON_DATA_ID] in data_ids:
                    data_entries.append((data_entry[JSON_DATA_ID], data_entry[JSON_LEAF_ID]))
                    data_ids_copy.remove(data_entry[JSON_DATA_ID])
                if not data_ids_copy:
                    break
        # Note that we return list of tuples!
        return data_entries

    def get_leaf_id(self, data_id):
        """
        Gets the mapping of a given data ID
        :param data_id: data ID
        :return: the mapping of a given data ID
        """
        return self.get_data_entries([data_id])[0][1]

    def update_leaf_id(self, data_id, is_uploaded):
        """
        Updates the mapping of data ID
        :param data_id: a data ID
        :param is_uploaded: a boolean value describing if the data block labeled by the given
        data ID is uploaded to the server's cloud
        :return:
        """
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
        """
        Chooses randomly new mapping for a given data block labeled by the given data ID
        :param data_id: a data ID
        :return:
        """
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
        """
        Checks if a data block labeled by the given data ID is in the PathORAM Tree or not,
        virtually checks if data ID is of an actual data block or of a dummy file
        :param data_id: a data ID
        :return:
        """
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_MODE) as loc_map:
            loc_data = json.load(loc_map)
            for data_entry in loc_data:
                if data_entry[JSON_DATA_ID] == data_id:
                    return True
            return False

    def count_data_ids(self):
        """
        Counts the amount of data blocks uploaded to the PathORAM Tree
        :return:
        """
        with data.open_data_file(utils.TREE_MAP_FILE_NAME, utils.READ_MODE) as loc_map:
            return len(json.load(loc_map))
