__author__ = 'ADillon'

import sys, socket

def serve(HOST="", PORT=8000):
    sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Socket created"
    sSocket.bind((HOST, PORT))
    print "Socket bound to (host, port): (" +repr(HOST) + ", " + str(PORT) + ")"
    sSocket.listen(5)
    print "Socket listening..."
    conn, addr = sSocket.accept()
    print "Connection made to:", addr
    conn.close()

if __name__ == "__main__":
    HOST = ""
    PORT = 8000

    if '-h' in sys.argv:
        try:
            HOST = sys.argv[sys.argv.index('-h') + 1]
        except:
            print "The '-h' flag must be followed by a host name"

    if '-p' in sys.argv:
        try:
            PORT = sys.argv[sys.argv.index('-p') + 1]
        except:
            print "The '-p' flag must be followed by a port number"

        try:
            PORT = int(PORT)
        except:
            print "The port must be an integer"
            PORT = 8000

    serve(HOST, PORT)