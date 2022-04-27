import math
from enum import Enum
import random

# Block size of the chunk files in terms of bytes
BLOCK_SIZE = 8192

# The height of the binary tree (as integer)
ORAM_HEIGHT = 2

# Numbering the leaves of the tree
MIN_LEAF = int(math.pow(2, ORAM_HEIGHT) - 1)
MAX_LEAF = int(math.pow(2, ORAM_HEIGHT + 1) - 2)

# for packing the data id
FORMAT_CHAR = '>Q'

# dummy data id
DUMMY_ID = 999999999999999


def get_random_leaf_id():
    return random.randrange(MIN_LEAF, MAX_LEAF + 1)
