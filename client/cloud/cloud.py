import os
import json

import client.data as data
import client.log as log
import client.cloud.utils as utils
import client.config as config
from client.cloud.exceptions import ErrorInCloudMap
import client.cloud.server_connection as server_connection

logger = log.get_logger(__name__)


class Cloud:
    def __init__(self, aes_crypto):
        if not data.data_file_exists(utils.CLOUD_MAP_FILE_NAME):
            logger.info("CREATE CLOUD MAP")
            self.create_cloud_map()
        cloud_init = self.load_cloup_map()
        self.aes_crypto = aes_crypto
        self.cloud_init = cloud_init

    def create_cloud_map(self):
        with data.open_data_file(utils.CLOUD_MAP_FILE_NAME, utils.WRITE_MODE) as cloud_map:
            json.dump({utils.JSON_INIT: False}, cloud_map, indent=utils.JSON_INDENT)

    def load_cloup_map(self):
        with data.open_data_file(utils.CLOUD_MAP_FILE_NAME, utils.READ_MODE) as cloud_map:
            try:
                cloud_data = json.load(cloud_map)
                return cloud_data[utils.JSON_INIT]
            except (ValueError, KeyError):
                logger.warning("ERROR IN CLOUD MAP")
                raise ErrorInCloudMap("Error in cloud map.")

    def update_cloud_map(self):
        with data.open_data_file(utils.CLOUD_MAP_FILE_NAME, utils.READ_WRITE_MODE) as cloud_map:
            cloud_data = json.load(cloud_map)
            cloud_data[utils.JSON_INIT] = self.cloud_init
            cloud_map.seek(utils.FILE_BEGIN)
            json.dump(cloud_data, cloud_map, indent=utils.JSON_INDENT)
            cloud_map.truncate()

    # create folder?

    # delete folder?

    def file_upload(self, content, block):
        server_connection.file_upload(content, self.get_path_to_file(block))

    def file_download(self, block):
        return server_connection.file_download(self.get_path_to_file(block))

    def get_path_to_file(self, node):
        return utils.FILE_NAME % node

    def setup_cloud(self, max_block_size):
        if not self.cloud_init:
            logger.info(f"START SETUP OF THE CLOUD WITH A TOTAL OF {max_block_size} BLOCKS")
            server_connection.socket_connect()
            for block in range(max_block_size):
                logger.info(f"UPLOAD FILE {block + 1}")
                self.file_upload(self.create_dummy_data(), block)
            logger.info("END SETUP OF THE CLOUD")
            self.cloud_init = True
            self.update_cloud_map()

    def create_dummy_data(self):
        dummy_id = config.DUMMY_ID
        dummy_data = os.urandom(config.BLOCK_SIZE)
        return self.aes_crypto.encrypt(dummy_id,dummy_data)

    def node_download(self, node):
        return self.file_download(node)

    def node_upload(self, node, content=None):
        if content is None:
            content = self.create_dummy_data()
        self.file_upload(content, node)
