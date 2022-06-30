## PathORAM Project
This a project I've done in a course named Advanced Topics in Online Privacy and Cybersecurity. This project consists of a client and a server, where the client can, under some storage restrictions, upload any file to the given server, through TCP/IP protocol, in encrypted way using the brilliant cryptographic data structure called PathORAM Tree. 

Some objectives I might implements in the future:
1. Threading for upload / downloading data blocks.
2. Supporting more entities to use a servers.
3.  Advanced UI
4.  Supporting more users

## Instructions
**Note**: only one user can use the program at a time. If a new user want to register, the program must be reset, as explained next.

To use the program, download the PathORAM folder and make sure that you install the requirements for this program from *requirements.txt*. Next, open a terminal in the PathORAM folder and activate the server in the following way:

    python3 server/server.py
If done successfully and the server is online, the following line should be printed:

    Server Waiting...
Now, for activating the client, one has to open a **new** terminal, while the **server is online**, and enter the following line:

    python3 main.py
Thereafter, please enter a password (in the next activations, the client has a saved file such that the password is saved and must to be used to use the program in the following attempts). After entering a password, instructions for using the program are printed. 

**Further Notes:**
For resetting the program, one has to open a terminal in the PathORAM folder and enter the following command, **only after terminating successfully both the client** (by entering the command: *quit*) **and the server** (by closing the terminal):

    python3 reset.py
This will result deleting all the map files and **all the stored data**. Note that after activation of the reset program, one has to enter a new password in order to use the program. **Do not run this line while the server is still running**. Please only do so after closing the server, simply by closing the terminal as mentioned above. Not doing so will result in bugs. 
## Credits
This project inspired greatly by [marcjulian](https://github.com/marcjulian)'s incredible [pyoram](https://github.com/marcjulian/pyoram) project.
