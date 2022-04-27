import os

import client.log as log
import client.ui.handler as handler

from getpass import getpass

WORK_DIR = os.getcwd()

logger = log.get_logger(__name__)

SIGNUP_MSG = "Welcome! Please enter a password to use the program. Note that once you entered as " \
             "password, this password will be permanent. You will have to reset manually the " \
             "program to use a new password."
WELCOME_MSG = "Hello. Please enter a password."
MANUAL_MSG = "You should upload files, one-by-one, which located in this folder, i.e. the folder " \
             "which the program runs from, *only*. Any downloaded file will also be " \
             "located in this folder. You can't upload files from anywhere else and you can't " \
             "download file to anywhere else. You can also delete files. \n" \
             "Commands:\nUpload: upload <filename>\n" \
             "Download: download <filename>\n" \
             "Delete: delete <filename>\n" \
             "Quit: quit"
INVALID_LENGTH_MSG = "Invalid command line length. Please re-enter your command."

COMMANDS = {"upload", "download", "delete"}

COMMAND_LINE_LENGTH = 2

def run():
    if not handler.has_signed_up():
        print(SIGNUP_MSG)
        terminated = False
        while not terminated:
            print("Please enter new password:")
            password = getpass("PASSWORD:")
            re_password = getpass("RE-PASSWORD:")
            if not password or not re_password:
                print("Password should be a string.")
            elif password != re_password:
                print("Passwords don't match. Please enter again.")
            else:
                handler.sign_up(password)
                handler.verify_password(password)
                terminated = True
    else:
        print(WELCOME_MSG)
        terminated = False
        while not terminated:
            try:
                password = getpass()
                handler.verify_password(password)
                terminated = True
            except Exception as err:
                logger.warning(err)
    handler.setup()
    print(MANUAL_MSG)
    while True:
        line = input("COMMAND: ").split()
        command = line[0]
        if command in COMMANDS and len(line) != COMMAND_LINE_LENGTH:
            logger.warning(INVALID_LENGTH_MSG)
        elif command == "quit":
            break
        elif command not in COMMANDS:
            logger.warning("Unrecognized command. Try again.")
        else:
            filename = line[1]
            try:
                if command == "upload":
                    handler.upload_file(WORK_DIR, filename)
                elif command == "download":
                    handler.download_file(WORK_DIR, filename)
                elif command == "delete":
                    handler.delete_file(filename)
            except Exception as e:
                logger.warning(e)


if __name__ == '__main__':
    run()
