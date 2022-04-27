WRITE_MODE = 'w'
READ_MODE = 'r'
READ_WRITE_MODE = 'r+'

SALT_LENGTH = 16
AES_LENGTH = 32
MAC_LENGTH = 32

LENGTH_ERR_MSG = "Master-Key %s must be %d URL-safe base64-encoded bytes."

KEY_MAP_FILE_NAME = 'key.map'

JSON_INDENT = 4


def str_to_byte(att):
    return att.encode()


def byte_to_str(att):
    return att.decode()
