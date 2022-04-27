import client.data as data
import client.crypto.utils as utils
from client.crypto.exceptions import KeyMapError

import json

JSON_SALT = "salt"
JSON_WRAPPED_AES_KEY = "wrapped_aes_key"
JSON_WRAPPED_MAC_KEY = "wrapped_mac_key"


class KeyMap:
    def __init__(self, salt, wrapped_aes_key, wrapped_mac_key):
        self.salt = salt
        self.wrapped_aes_key = wrapped_aes_key
        self.wrapped_mac_key = wrapped_mac_key

    def save_to_file(self):
        with data.open_data_file(utils.KEY_MAP_FILE_NAME, utils.WRITE_MODE) as key_map:
            salt = utils.byte_to_str(self.salt)
            wrapped_aes_key = utils.byte_to_str(self.wrapped_aes_key)
            wrapped_mac_key = utils.byte_to_str(self.wrapped_mac_key)
            json.dump({JSON_SALT: salt, JSON_WRAPPED_AES_KEY: wrapped_aes_key,
                       JSON_WRAPPED_MAC_KEY: wrapped_mac_key}, key_map, indent=utils.JSON_INDENT,
                      sort_keys=True)

    @classmethod
    def load_from_file(cls):
        with data.open_data_file(utils.KEY_MAP_FILE_NAME, utils.READ_MODE) as key_map:
            try:
                json_key_map = json.load(key_map)
                salt = utils.str_to_byte(json_key_map[JSON_SALT])
                wrapped_aes_key = utils.str_to_byte(json_key_map[JSON_WRAPPED_AES_KEY])
                wrapped_mac_key = utils.str_to_byte((json_key_map[JSON_WRAPPED_MAC_KEY]))
                key_file = KeyMap(salt, wrapped_aes_key, wrapped_mac_key)
                return key_file
            except (ValueError, KeyError):
                raise KeyMapError("key.map might be empty or the data is not a valid JSON format.")

    @classmethod
    def verify_content(cls):
        try:
            cls.load_from_file()
            return True
        except KeyMapError:
            return False
