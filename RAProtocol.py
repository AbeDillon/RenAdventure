__author__ = 'ADillon'

import socket

def sendMessage(message, conn):
    """

    """
    prefix = encodePrefix(message)
    message = prefix + message
    conn.sendall(message)

def receiveMessage(conn):
    """

    """
    prefix = conn.recv(4)
    msg_len = decodePrefix(prefix)
    message = ""
    while msg_len > 0:
        if msg_len > 4096:
            message += conn.recv(4096)
            msg_len -= 4096
        else:
            message += conn.recv(msg_len)
            msg_len = 0
            
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


