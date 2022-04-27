import math

import client.log as log
from client.storage.exceptions import DummyFileFound
import client.config as config
from client.cloud.cloud import Cloud
from client.storage.stash import Stash
from client.storage.tree_map import TreeMap

logger = log.get_logger(__name__)


class PathORAM:
    MAX_ORAM_BLOCK_SIZE = int(math.pow(2, config.ORAM_HEIGHT + 1) - 1)
    MAX_ORAM_STORAGE_SIZE = MAX_ORAM_BLOCK_SIZE * config.BLOCK_SIZE

    def __init__(self, aes_crypto):
        self.cloud = Cloud(aes_crypto)
        self.aes_crypto = aes_crypto

    @classmethod
    def get_max_oram_block_size(cls):
        return cls.MAX_ORAM_BLOCK_SIZE

    @classmethod
    def get_max_oram_storage_size(cls):
        return cls.MAX_ORAM_STORAGE_SIZE

    def setup_cloud(self):
        self.cloud.setup_cloud(self.get_max_oram_block_size())

    def path_to_leaf(self, leaf):
        path = [0] * (config.ORAM_HEIGHT + 1)
        min_leaf = config.MIN_LEAF
        max_leaf = config.MAX_LEAF
        for cur_level in range(config.ORAM_HEIGHT):
            # binary search
            mid = ((max_leaf - min_leaf) // 2) + min_leaf
            if leaf <= mid:
                path[cur_level + 1] = (path[cur_level] * 2) + 1
                max_leaf = mid
            else:
                path[cur_level + 1] = (path[cur_level] * 2) + 2
                min_leaf = mid + 1
        return path

    def path_to_root(self, leaf):
        return self.path_to_leaf(leaf)[::-1]

    def get_potential_data_entries(self):
        potential_data_ids = Stash().get_potential_data_ids()
        return TreeMap().get_data_entries(potential_data_ids)

    def read_node(self, node):
        return self.cloud.node_download(node)

    def write_node(self, node, data_file=None):
        self.cloud.node_upload(node, data_file)

    def decrypt_data_block(self, token):
        # Note - we return here a tuple! (data_id, plaintext)
        return self.aes_crypto.decrypt(token)

    def read_path(self, path_to_root):
        data_blocks = list()
        for node in path_to_root:
            logger.info(f"READ PATH - DOWNLOADING FROM NODE {node}")
            data_block = self.read_node(node)
            data_blocks.append(data_block)
        return data_blocks

    def write_stash(self, downloaded_data_blocks, wanted_data_file_id=None):
        wanted_data_block = None
        for data_block in downloaded_data_blocks:
            try:
                data_id, plaintext = self.decrypt_data_block(data_block)
                if TreeMap().data_id_exist(data_id):
                    logger.info(f"WRITE STASH - DOWNLOADED DATA FILE WITH ID {data_id}")
                    token = self.aes_crypto.encrypt(data_id, plaintext)
                    Stash().add_file(data_id, token)
                    if wanted_data_file_id is not None and wanted_data_file_id == data_id:
                        TreeMap().choose_fresh_leaf_id(data_id)
                        wanted_data_block = data_id, plaintext
                    else:
                        TreeMap().update_leaf_id(data_id, False)
            except DummyFileFound:
                logger.info("WRITE STASH - DOWNLOADED DUMMY FILE")
                pass
        return wanted_data_block

    def write_path(self, path_to_root):
        # Note that the algorithm implemented here is as described in the paper of Stefanov et al.
        # As such, there is no eviction per say, but there is indeed a way of handling overflows.
        for node in path_to_root:
            potential_data_entries = self.get_potential_data_entries()
            is_potential_data_block = False
            for potential_data_entry in potential_data_entries:
                potential_leaf_id = abs(potential_data_entry[1])
                potential_path = self.path_to_root(potential_leaf_id)
                if node in potential_path:
                    is_potential_data_block = True
                    # Recall that data property = (data_id, leaf_id)
                    data_id = potential_data_entry[0]
                    data_block = Stash().get_data_block(data_id)
                    # Write to the server
                    self.write_node(node, data_block[1])
                    logger.info(f"WRITE PATH - UPLOAD TO NODE {node} DATA BLOCK WITH ID {data_id}")
                    TreeMap().update_leaf_id(data_id, True)
                    Stash().delete_data_block(data_id)
                    break
                if not is_potential_data_block:
                    self.write_node(node)
                    logger.info(f"WRITE PATH - UPLOAD TO NODE {node} DUMMY DATA BLOCK")

    def access(self, path_to_root, wanted_data_id=None):
        read_path_data_blocks = self.read_path(path_to_root)
        data_block = self.write_stash(read_path_data_blocks, wanted_data_id)
        self.write_path(path_to_root)
        logger.info(f"STASH SIZE - {Stash().size}")
        return data_block

    def download(self, data_ids):
        data_blocks = list()
        for data_id in data_ids:
            leaf_id = TreeMap().get_leaf_id(data_id)
            # in stash
            if leaf_id < 0:
                data_block = Stash().get_data_block(data_id)
                logger.info("PATH ORAM - ACCESS STASH")
                ciphertext = data_block[1]
                data_block = self.decrypt_data_block(ciphertext)
            # in server
            else:
                path_to_root = self.path_to_root(leaf_id)
                data_block = self.access(path_to_root, data_id)
            data_blocks.append(data_block)
        return data_blocks

    def update(self, data_entries):
        for data_entry in data_entries:
            leaf_id = abs(data_entry[1])
            path_to_root = self.path_to_root(leaf_id)
            self.access(path_to_root)
