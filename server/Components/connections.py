import socket
import enum

class status(enum.IntEnum):
    Wait = 0,
    Live = 1

class connection:
    def __init__(self, address: str, con: socket.socket):
        self.connection = con
        self.status: status = status.Wait
        self.data = {'address': address}
