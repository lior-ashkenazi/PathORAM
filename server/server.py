import socket
import os
import tqdm
import utils


SEPARATOR = "<THIS_TEXT_JUST_DISTINGUISH_TEXTS>"
s = socket.socket()
s.bind(("127.0.0.1", 1234))
s.listen(1)

while True:
    print("Server waiting...")
    if not os.path.exists(utils.DATA_DIR):
        os.makedirs(utils.DATA_DIR)
    c, _ = s.accept()
    msg = c.recv(utils.HEADER_SIZE)
    if str(msg.decode("utf-8")) == "upload":
        try:
            data = c.recv(utils.CHUNK_SIZE).decode()
            filename, size = data.split(SEPARATOR)
            filename = os.path.basename(filename)
            filename = os.path.join(utils.DATA_DIR, filename)
            file = open(filename, 'wb')
            terminated = False
            upload_bar = tqdm.tqdm(range(int(size)), f"Receiving {filename}", unit="B",
                                   unit_scale=True, unit_divisor=1024)
            while not terminated:
                data = c.recv(utils.CHUNK_SIZE)
                if not data:
                    terminated = True
                    break
                file.write(data)
                upload_bar.update(len(data))
            file.close()
        except:
            pass

    if str(msg.decode("utf-8")) == "download":
        try:
            data = str(c.recv(utils.CHUNK_SIZE).decode("utf-8"))
            filename = str(data)
            filename = os.path.join(utils.DATA_DIR, filename)
            size = os.path.getsize(filename)
            c.send(f"{filename}{SEPARATOR}{size}".encode())
            upload_bar = tqdm.tqdm(range(int(size)), f"Sending {filename}", unit="B",
                                   unit_scale=True, unit_divisor=1024)
            file = open(filename, 'rb')
            terminated = False
            while not terminated:
                data = file.read(utils.CHUNK_SIZE)
                if not data:
                    c.close()
                    terminated = False
                c.sendall(data)
                upload_bar.update(len(data))
            file.close()
        except:
            pass
