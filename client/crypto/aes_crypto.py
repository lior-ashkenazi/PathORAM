import base64
import os
import struct

import six
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap, InvalidUnwrap

import client.config as config
import client.crypto.utils as utils
from client.crypto.key_map import KeyMap
from client.crypto.exceptions import WrongPassword, DummyFileFound, InvalidToken


class AESCryptography():
    def __init__(self, key_file, password, backend=None):
        if backend is None:
            backend = default_backend()

        salt = self.from_base64(key_file.salt)
        wrapped_aes_key = self.from_base64(key_file.wrapped_aes_key)
        wrapped_mac_key = self.from_base64(key_file.wrapped_mac_key)

        if len(salt) != utils.SALT_LENGTH:
            raise ValueError(utils.LENGTH_ERR_MSG % ("Salt", utils.SALT_LENGTH))

        master_key = self.generate_key(password, salt)
        self.aes_key = self.unwrap_key(master_key, wrapped_aes_key)
        self.mac_key = self.unwrap_key(master_key, wrapped_mac_key)
        self.backend = backend

        if len(self.aes_key) != utils.AES_LENGTH:
            raise ValueError(utils.LENGTH_ERR_MSG % ("AES", utils.AES_LENGTH))

        if len(self.aes_key) != utils.MAC_LENGTH:
            raise ValueError(utils.LENGTH_ERR_MSG % ("MAC", utils.MAC_LENGTH))

    @classmethod
    def add_padding(cls, plaintext, block_size):
        padder = padding.PKCS7(block_size).padder()
        return padder.update(plaintext) + padder.finalize()

    @classmethod
    def remove_padding(cls, padded_plaintext, block_size):
        unpadder = padding.PKCS7(block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext)
        try:
            plaintext += unpadder.finalize()
        except ValueError:
            raise InvalidToken
        return plaintext

    @classmethod
    def to_base64(cls, att):
        return base64.urlsafe_b64encode(att)

    @classmethod
    def from_base64(cls, att):
        return base64.urlsafe_b64decode(att)

    @classmethod
    def generate_key(cls, password, salt):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=utils.MAC_LENGTH, salt=salt,
                         iterations=100000, backend=default_backend())
        return kdf.derive(password.encode())

    @classmethod
    def generate_random_key(cls):
        return os.urandom(utils.AES_LENGTH)

    @classmethod
    def wrap_key(cls, wrapping_key, key_to_wrap):
        return aes_key_wrap(wrapping_key, key_to_wrap, default_backend())

    @classmethod
    def create_keys(cls, password):
        salt = os.urandom(utils.SALT_LENGTH)
        master_key = cls.generate_key(password, salt)

        aes_key = cls.generate_random_key()
        mac_key = cls.generate_random_key()

        wrapped_aes_key = cls.wrap_key(master_key, aes_key)
        wrapped_mac_key = cls.wrap_key(master_key, mac_key)

        return KeyMap(cls.to_base64(salt), cls.to_base64(wrapped_aes_key),
                      cls.to_base64(wrapped_mac_key))

    def unwrap_key(self, wrapping_key, key_to_unwrap):
        try:
            return aes_key_unwrap(wrapping_key, key_to_unwrap, default_backend())
        except InvalidUnwrap:
            raise WrongPassword("Password is incorrect.")

    def encrypt(self, data_id, data):
        iv = os.urandom(16)

        if not isinstance(data_id, int):
            raise TypeError("Data ID must be integer.")

        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes.")

        # Note that we pack with the plaintext a prefix which includes the data ID
        main_parts = (struct.pack(config.FORMAT_CHAR, data_id) + data)
        padded_data = self.add_padding(main_parts, algorithms.AES.block_size)
        encryptor = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv),
                           backend=self.backend).encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        basic_parts = (b"\x80" + iv + ciphertext)

        h = HMAC(self.mac_key, hashes.SHA256(), backend=self.backend)
        h.update(basic_parts)
        hmac = h.finalize()
        return basic_parts + hmac

    def decrypt(self, token):
        if not isinstance(token, bytes):
            raise TypeError("Ciphertext must be bytes.")

        if not token or six.indexbytes(token, 0) != 0x80:
            raise InvalidToken

        hmac = token[-32:]
        h = HMAC(self.mac_key, hashes.SHA256(), backend=self.backend)
        h.update(token[:-32])
        try:
            h.verify(hmac)
        except InvalidSignature:
            raise InvalidToken

        iv = token[1:17]
        ciphertext = token[17:-32]
        decryptor = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv), self.backend).decryptor()
        padded_plaintext = decryptor.update(ciphertext)
        try:
            padded_plaintext += decryptor.finalize()
        except ValueError:
            raise InvalidToken

        plaintext = self.remove_padding(padded_plaintext, algorithms.AES.block_size)

        try:
            data_id = struct.unpack(config.FORMAT_CHAR, plaintext[:8])
        except struct.error:
            raise InvalidToken

        if data_id == config.DUMMY_ID:
            raise DummyFileFound

        data = plaintext[8:]
        return data_id[0], data