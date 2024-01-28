import socket
import enum

class Status(enum.IntEnum):
    Wait = 0,
    Live = 1

class Connection:
    def __init__(self, address: str, con: socket.socket):
        self.connection = con
        self.status: Status = Status.Wait
        self.data = {'address': address}
