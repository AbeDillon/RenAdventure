__author__ = 'ADillon'

import socket
import sys
import pickle
from PyQt4 import QtNetwork, QtCore

def sendMessage(message, conn):
    """

    """
    message_str = pickle.dumps(message)
    prefix = encodePrefix(message_str)
    out_message = prefix + message_str
    if isinstance(conn, socket.socket):
        conn.sendall(out_message)
    else:
        conn.writeData(out_message)

def receiveMessage(conn):
    """

    """
    if isinstance(conn, socket.socket):
        prefix = conn.recv(4)
    else:
        prefix = conn.readData(4)
    msg_len = decodePrefix(prefix)
    message_str = ""
    while msg_len > 4096:
        if isinstance(conn, socket.socket):
            message_str += conn.recv(4096)
        else:
            message_str += conn.readData(4096)
        msg_len -= 4096

    if isinstance(conn, socket.socket):
        message_str += conn.recv(msg_len)
    else:
        message_str += conn.readData(msg_len)

    message = pickle.loads(message_str)
    return message

def encodePrefix(message):
    """

    """
    # Get the length of the message
    msg_len = len(message)

    # Convert the length to a 4-character prefix
    prefix = ""
    for i in range(4):
        char = chr(msg_len % 256) # convert the last byte to a character
        prefix += char            # add the character to the prefix
        msg_len /= 256            # remove the last byte

    # Reverse the prefix
    prefix = prefix[::-1]

    return prefix

def decodePrefix(prefix):
    """

    """
    msg_len = ord(prefix[0])
    for i in range(1,4):
        msg_len *= 256
        msg_len += ord(prefix[i])

    return msg_len

class QtCommand(QtCore.QObject):

   def __init__(self, name=None, tags=None, body=None, art=None, status=None, tabs=None, sound=None, parent=None):
       super(QtCommand, self).__init__(parent)
       self.name = name
       self.tags = tags
       self.body = body
       self.art = art
       self.status = status
       self.tabs = tabs
       self.sound = sound

   def __init__(self, commandObj):
        super(QtCommand, self).__init__()
        self.name = commandObj.name
        self.tags = commandObj.tags
        self.body = commandObj.body

class command(object):
    def __init__(self, name=None, tags=None, body=None):
        self.name = name
        self.tags = tags
        self.body = body

    def __init__(self, QtCommandObj):
        self.name = QtCommandObj.name
        self.tags = QtCommandObj.tags
        self.body = QtCommandObj.body