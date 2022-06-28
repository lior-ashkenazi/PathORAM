import socket
import tqdm
import os
import time

import client.data as data
import client.cloud.utils as utils

CLIENT_DIR = data.BASE_DIR
SEPARATOR = "<THIS_TEXT_JUST_DISTINGUISH_TEXTS>"


def socket_connect():
    global s
    ip = "127.0.0.1"
    port = 1234
    s = socket.socket()
    s.connect((ip, port))


def file_upload(content, filename):
    filename = os.path.join(CLIENT_DIR, filename)
    with open(filename, 'wb') as f:
        f.write(content)
    size = os.path.getsize(filename)
    s.send(bytes("upload", "utf-8"))
    s.send(f"{filename}{SEPARATOR}{size}".encode())
    upload_bar = tqdm.tqdm(range(int(size)), f"Sending {filename}", unit="B", unit_scale=True,
                           unit_divisor=1024)
    f = open(filename, 'rb')
    f.seek(utils.FILE_BEGIN)
    terminated = False
    while not terminated:
        data = f.read(4096)
        if not data:
            s.close()
            time.sleep(0.5)
            socket_connect()
            terminated = True
        s.sendall(data)
        upload_bar.update(len(data))
    f.close()
    os.remove(filename)


def file_download(filename):
    s.send(bytes("download", "utf-8"))
    s.send(bytes(filename, "utf-8"))
    data = s.recv(4096).decode()
    filename, size = data.split(SEPARATOR)
    filename = os.path.basename(filename)
    upload_bar = tqdm.tqdm(range(int(size)), f"Receiving {filename}", unit="B", unit_scale=True,
                           unit_divisor=1024)
    tmp_filename = os.path.join(CLIENT_DIR, 'tmp')
    f = open(tmp_filename, 'wb')
    while True:
        data = s.recv(4096)
        if not data:
            time.sleep(0.1)
            socket_connect()
            break
        f.write(data)
        upload_bar.update(len(data))
    f.close()
    f = open(tmp_filename, 'rb')
    f.seek(utils.FILE_BEGIN)
    data = f.read()
    f.close()
    os.remove(tmp_filename)
    return data
