__author__ = 'ADillon'

import sys, socket
import time

def connect(HOST="54.244.118.196", PORT=8000):
    cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Socket created."
    print "Attempting to connect to (host, port): (" + repr(HOST) + ", " + str(PORT) + ")"
    cSocket.connect((HOST, PORT))
    print "Socket connected."
    cSocket.close()

if __name__ == "__main__":
    HOST = "54.244.118.196"
    PORT = 80

    if "-h" in sys.argv:
        try:
            HOST = sys.argv[sys.argv.index("-h") + 1]
        except:
            print "The '-h' flag must be followed by a host name."

    if "-p" in sys.argv:
        try:
            PORT = sys.argv[sys.argv.index("-p") + 1]
        except:
            print "The '-p' flag must be followed by a port number."

        try:
            PORT = int(PORT)
        except:
            print "The port must be an integer."
            PORT = 8000

    connect(HOST, PORT)

    t = time.time() + 2
    while time.time() < t:
        pass