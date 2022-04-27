import client.log as log
import client.config as config
from client.storage.data_file_map import DataFileMap
from client.storage.tree_map import TreeMap
from client.storage.stash import Stash
from client.storage.exceptions import FileSizeError

logger = log.get_logger(__name__)

PADDING = b'0'


class FileProcessor:
    def __init__(self, aes_crypto=None):
        self.aes_crypto = aes_crypto
        self.data_id_counter = DataFileMap().get_id_counter()

    def split(self, file_name, file_input):
        logger.info(f"LENGTH OF THE SELECTED FILE {len(file_input)}")
        data_ids = []
        for buffer in range(0, len(file_input), config.BLOCK_SIZE):
            if self.data_id_counter == config.DUMMY_ID:
                self.data_id_counter += 1
            data_id = self.data_id_counter
            self.data_id_counter += 1
            data_ids.append(data_id)
            chunk = file_input[buffer:buffer + config.BLOCK_SIZE]
            logger.info(f"CHUNK SIZE IS {len(chunk)} AFTER SPLITTING")
            if len(chunk) != config.BLOCK_SIZE:
                logger.info("CHUNK IS SMALLER THAN THE BLOCK SIZE - ADDING PADDING")
                chunk = chunk.rjust(config.BLOCK_SIZE, PADDING)
                logger.info(f"CHUNK SIZE {len(chunk)} AFTER PADDING")
            token = self.aes_crypto.encrypt(data_id, chunk)
            logger.info(f"CHUNK SIZE IS {len(token)} AFTER ENCRYPTION")
            Stash().add_file(data_id, token)
            TreeMap().add_data(data_id)
        DataFileMap().add_data_file(file_name, len(file_input), data_ids, self.data_id_counter)

    def join(self, data_blocks, expected_file_len):
        plaintext = bytearray()
        for pos, data_block in enumerate(data_blocks):
            logger.info(f"JOINING DATA BLOCK WITH ID {data_block[0]}")
            plaintext_chunk = data_block[1]
            if pos == len(data_blocks) - 1:
                remaining_len = expected_file_len - len(plaintext)
                plaintext_chunk = plaintext_chunk[-remaining_len:]
                logger.info(f"UNPADDING THE CHUNK WITH ID {data_block[0]}")
            plaintext.extend(plaintext_chunk)

        if expected_file_len != len(plaintext):
            raise FileSizeError("File size of the downloaded file is not correct.")

        return plaintext
