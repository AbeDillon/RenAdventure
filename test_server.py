__author__ = 'ADillon'

import sys, socket

def serve(HOST="", PORT=1337):
    sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print "Socket created"
    sSocket.bind((HOST, PORT))
    #print "Socket bound to (host, port): (" +repr(HOST) + ", " + str(PORT) + ")"
    sSocket.listen(5)
    #print "Socket listening..."
    conn, addr = sSocket.accept()
    #print "Connection made to:", addr
    data = conn.recv(1024)
    msg = ""
    while data != None:
        msg += data
        data = conn.recv(1024)
    #print msg
    #print "Sending response"
    conn.sendall("WORLD!")
    conn.close()

if __name__ == "__main__":
    HOST = ""
    PORT = 1337

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
            PORT = 1337

    serve(HOST, PORT)