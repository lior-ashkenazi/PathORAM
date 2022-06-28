import math

import client.log as log
from client.storage.exceptions import DummyFileFound
import client.config as config
from client.cloud.cloud import Cloud
from client.storage.stash import Stash
from client.storage.tree_map import TreeMap

logger = log.get_logger(__name__)


class PathORAM:
    """
    The PathORAM Tree which facilitates the protocol for which the user uploads file to the server
    """
    # The maximal size amounts of block in the PathORAM Tree
    MAX_ORAM_BLOCK_SIZE = int(math.pow(2, config.ORAM_HEIGHT + 1) - 1)

    # The maximal storage the PathORAM Tree can contain
    MAX_ORAM_STORAGE_SIZE = MAX_ORAM_BLOCK_SIZE * config.BLOCK_SIZE

    def __init__(self, aes_crypto):
        self.cloud = Cloud(aes_crypto)
        self.aes_crypto = aes_crypto

    @classmethod
    def get_max_oram_block_size(cls):
        """
        Returns the maximal size amounts of block in the PathORAM Tree
        :return: maximal size amounts of block in the PathORAM Tree
        """
        return cls.MAX_ORAM_BLOCK_SIZE

    @classmethod
    def get_max_oram_storage_size(cls):
        """
        Returns the maximal storage the PathORAM can contain
        :return: the maximal storage the PathORAM can contain
        """
        return cls.MAX_ORAM_STORAGE_SIZE

    def setup_cloud(self):
        """
        Sets up the server's cloud
        :return:
        """
        self.cloud.setup_cloud(self.get_max_oram_block_size())

    def path_to_leaf(self, leaf):
        """
        Computing the path to a leaf, that is the nodes needed to be traversed in order to reach
        the given leaf
        :param leaf: a leaf in the PathORAM tree
        :return: the path to a leaf, that is the nodes needed to be traversed in order to reach
        the given leaf
        """
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
        """
        Returns the path to the root from a given leaf
        :param leaf: a leaf in the PathORAM tree
        :return: the path to the root from a given leaf
        """
        return self.path_to_leaf(leaf)[::-1]

    def get_potential_data_entries(self):
        """
        Returns the potential data entries
        :return: potential data entries
        """
        potential_data_ids = Stash().get_potential_data_ids()
        return TreeMap().get_data_entries(potential_data_ids)

    def decrypt_data_block(self, token):
        """
        Decrypts data block
        :param token: a data block, labeled token
        :return: tuple (data_id, plaintext)
        """
        # Note - we return here a tuple! (data_id, plaintext)
        return self.aes_crypto.decrypt(token)

    def upload(self, data_entries):
        """
        Upload data blocks, represented by data entries
        :param data_entries: data entries - tuples of data ids and the leaves they mapped unto
        :return:
        """
        for data_entry in data_entries:
            leaf_id = abs(data_entry[1])
            path_to_root = self.path_to_root(leaf_id)
            self._access(path_to_root)

    def download(self, data_ids):
        """
        Downloads data blocks, given data ids
        :param data_ids: data ids
        :return: data blocks
        """
        data_blocks = list()
        for data_id in data_ids:
            leaf_id = TreeMap().get_leaf_id(data_id)
            # in stash
            if leaf_id < 0:
                logger.info("PATH ORAM - ACCESS STASH")
                tagged_data_block = Stash().get_data_block(data_id)
                ciphertext = tagged_data_block[1]
                data_block = self.decrypt_data_block(ciphertext)
            # in server
            else:
                path_to_root = self.path_to_root(leaf_id)
                data_block = self._access(path_to_root, data_id)
            data_blocks.append(data_block)
        return data_blocks

    def _access(self, path_to_root, wanted_data_id=None):
        """
        Accesses the PathORAM tree, given a path to the root and potentially a data block of a
        wanted data file
        :param path_to_root: a list of notes which consists a path to the root
        :param wanted_data_id: a data block labeled with an ID that potentially we want to get
        :return: a data block - could be "garbage" data block or a data block we actually want to
        join into a file
        """
        read_path_data_blocks = self._read_path(path_to_root)
        data_block = self._write_stash(read_path_data_blocks, wanted_data_id)
        self._write_path(path_to_root)
        logger.info(f"STASH SIZE - {Stash().size}")
        return data_block

    def _read_path(self, path_to_root):
        """
        The Read Path in the algorithm of maintaining the tree as described in the paper of
        Stefanov et al.
        :param path_to_root: a list of notes which consists a path to the root
        :return: data blocks
        """
        data_blocks = list()
        for node in path_to_root:
            logger.info(f"READ PATH - DOWNLOADING FROM NODE {node}")
            data_block = self._read_node(node)
            data_blocks.append(data_block)
        return data_blocks

    def _read_node(self, node):
        """
        Reads a node from the server's cloud, that is, a data block, as each node in the PathORAM
        tree is in fact a data block
        :param node: a node in the PathORAM tree which is in fact a data block
        :return: the data block (as data)
        """
        return self.cloud.node_download(node)

    def _write_stash(self, downloaded_data_blocks, wanted_data_file_id=None):
        """
        The Write Stash in the algorithm of maintaining the tree as described in the paper of
        :param downloaded_data_blocks: downloaded data blocks from the server's cloud
        :param wanted_data_file_id: a data file labeled with ID we potentially would want to draw
        from the tree
        :return: None if not data block is desired, else an actual data block
        """
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

    def _write_path(self, path_to_root):
        """
        The Write Path in the algorithm of maintaining the tree as described in the paper of
        :param path_to_root: a list of notes which consists a path to the root
        :return:
        """
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
                    # Recall that data entry = (data_id, leaf_id)
                    data_id = potential_data_entry[0]
                    data_block = Stash().get_data_block(data_id)
                    # Write to the server
                    self._write_node(node, data_block[1])
                    logger.info(f"WRITE PATH - UPLOAD TO NODE {node} DATA BLOCK WITH ID {data_id}")
                    # Update leaf ID means the leaf ID will be updated to positive to denote that
                    # the data block uploaded to server (as it was negative before)
                    TreeMap().update_leaf_id(data_id, True)
                    Stash().delete_data_block(data_id)
                    break
                if not is_potential_data_block:
                    # Write dummy data block to that node instead
                    self._write_node(node)
                    logger.info(f"WRITE PATH - UPLOAD TO NODE {node} DUMMY DATA BLOCK")

    def _write_node(self, node, data_file=None):
        """
        Uploads a PathORAM node to the server's cloud, that is, a data block
        :param node: a node in the PathORAM tree
        :param data_file: a data file if exists, else None
        :return:
        """
        self.cloud.node_upload(node, data_file)
