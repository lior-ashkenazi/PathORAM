import os
import shutil

from client.storage import utils as storage_utils
from client.cloud import utils as cloud_utils
from client.crypto import utils as crypto_utils
from client.data import BASE_DIR, STASH_DIR

from server.utils import DATA_DIR

CLOUD_MAP_PATH = os.path.join(BASE_DIR, cloud_utils.CLOUD_MAP_FILE_NAME)
FILE_MAP_PATH = os.path.join(BASE_DIR, storage_utils.FILE_MAP_FILE_NAME)
KEY_MAP_PATH = os.path.join(BASE_DIR, crypto_utils.KEY_MAP_FILE_NAME)
LOG_FILE_PATH = os.path.join(BASE_DIR, storage_utils.LOG_FILE_NAME)
TMP_FILE_PATH = os.path.join(BASE_DIR, 'tmp')
TREE_MAP_PATH = os.path.join(BASE_DIR, storage_utils.TREE_MAP_FILE_NAME)
FILES = [CLOUD_MAP_PATH, FILE_MAP_PATH, KEY_MAP_PATH, LOG_FILE_PATH, TMP_FILE_PATH, TREE_MAP_PATH]

if __name__ == '__main__':
    # --------------- server ---------------------
    shutil.rmtree(DATA_DIR, ignore_errors=True)
    # --------------------------------------------

    # --------------- client ---------------------
    shutil.rmtree(STASH_DIR, ignore_errors=True)
    for filename in FILES:
        try:
            os.remove(filename)
        except OSError:
            pass
    # --------------------------------------------
