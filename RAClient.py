__author__ = 'AYeager'

from PyQt4 import QtGui, QtCore, QtNetwork
import socket, ssl
import sys
import RenA
import Queue
import RAProtocol
import pickle

#address = QtNetwork.Q
_Local_Host = socket.gethostname()
_Local_Host = socket.gethostbyname(_Local_Host)# replace with actual host address
#_Local_Host = QtNetwork.QHostAddress(_Local_Host)
_Server_Host = socket.gethostname() #'54.244.118.196' # replace with actual server address
_Login_Port = 60005


class MainDialog(QtGui.QDialog, RenA.Ui_mainDialog):
    """main GUI object"""

    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        global _Local_Host
        global _Server_Host
        global _Login_Port
        self.localHost = _Local_Host
        self.serverHost = _Server_Host
        self.lPort = _Login_Port
        self.iPort = ""
        self.oPort = ""
        self.loggedIn = False
        self.name = ""

        self.oldStyle = True
        self.setupUi(self)

        # build input and output objects
        self.inQueue = Queue.Queue()
        self.outQueue = Queue.Queue()

        # Local Server Build
        #self.initServer()

        # Connections/Signals
        self.connect(self, QtCore.SIGNAL("mainDisplay(QString)"), self.appendDisplay, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("inputBox(QObject)"), self.fillTabs, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("artBox(QObject)"), self.appendArt, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("statusBox(QObject)"), self.appendStatus, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("playSound(QObject)"), self.playSound, QtCore.Qt.DirectConnection)
        #self.connect(self, QtCore.SIGNAL("readySend(QString)"), self.sendMessage, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("sendOld"), self.sendMessage, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("readySend(QString)"), self.sendMessage, QtCore.Qt.DirectConnection)
        self.inputBox.returnPressed.connect(self.getUserInput)
        #self.connect(self.tcpServer, QtCore.SIGNAL("newConnection()"), self.handleNewConnection)

        self.mainDisplay.append('\n'*25+" "*10+'Welcome to the Ren Adventure!!'+'\n'*15)
        self.inputBox.setFocus()
        self.main()

    def initServer(self):
        self.tcpServer = QtNetwork.QTcpServer()
        self.tcpServer.listen(self.localHost, self.port)

    def outSocket(self):

        if self.loggedIn == False:
            port = self.lPort
        else:
            port = self.oPort

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem')
        ssl_sock.connect((_Server_Host, port))
        return ssl_sock

    def handleNewConnection(self):

        while self.tcpServer.hasPendingConnections():
            connection = self.tcpServer.nextPendingConnection()
            connection.setLocalCertificate('cert.pem')
            message = RAProtocol.receiveMessage(connection)
            if hasattr(message, "tags"):
                if "mainDisplay" in message.tags:
                    self.emit(QtCore.SIGNAL("mainDisplay(QString)"), message.body )
                if "inputBox" in message.tags:
                    self.emit(QtCore.SIGNAL("inputBox(RAProtocol.command)"), message)
                if "artBox" in message.tags:
                    self.emit(QtCore.SIGNAL("artBox(RAProtocol.command)"), message)
                if "statusBox" in message.tags:
                    self.emit(QtCore.SIGNAL("statusBox(RAProtocol.command)"), message)
                if "playSound" in message.tags:
                    self.emit(QtCore.SIGNAL("playSound(RAProtocol.command)"), message)
                if "login" in message.tags:
                    if message.body == "accepted":
                        self.loggedIn = True
                    else:
                        self.emit(QtCore.SIGNAL("mainDisplay(QString)"), 'Log-in failed.\nEnter User Name.')
            else:
                self.emit(QtCore.SIGNAL("mainDisplay(QString)"), message )

    def main(self):

        self.emit(QtCore.SIGNAL("mainDisplay(QString)"), 'Enter User Name.')


    def appendDisplay(self, message):

        self.mainDisplay.append(message)

    def fillTabs(self):
        pass

    def appendStatus(self, message):
        pass

    def appendArt(self, message):
        self.artBox.clear()
        self.artBox.append(message.body)

    def playSound(self):
        pass

    def getUserInput(self):
        """Captures and distributes User input from inputBox"""
        line = self.inputBox.displayText()

        if line != "":
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), line )
            self.inputBox.clear()
            self.inputBox.setFocus()
            if not self.loggedIn:
               self.login(line)
            else:
                if self.oldStyle == True:
                    message = (str(self.name), str(line), [])
                    #self.emit(QtCore.SIGNAL("sendOld"), message)
                else:
                    message = RAProtocol.command(name= str(self.name), body=str(line))
                message = pickle.dumps(message)
                self.emit(QtCore.SIGNAL("readySend(QString)"), message)

    def sendMessage(self, message):

        message = str(message)
        message = pickle.loads(message)
        outSocket = self.outSocket()
        if self.oldStyle == False:
            # convert message object from QObject to regular object so RAP can handle properly
            message = RAProtocol.command(message)
        print message
        RAProtocol.sendMessage(message, outSocket)
        outSocket.close()

    def login(self, line):
         if self.name == "":
            self.name= line
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "Enter Password" )
         else:
            self.password = line
            loginMessage = RAProtocol.QtCommand(tags=['login'], body= self.name + " " + self.password)
            #self.emit(QtCore.SIGNAL("readySend(QObject)"), loginMessage)  #  Will likely be used in single port build
            self.connect_to_server(loginMessage)

            # ports = self.connect_to_server(loginMessage)  ##  moving this functionality to connect to server
            # if ports in ['invalid', 'banned_name', "affiliation_get"]:
            #     self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "That login is invalid.  Again." )
            #     self.nameGotten = False
            #     self.name = None
            #     self.password = None
            # else:
            #     return ports



    def connect_to_server(self, line):  #  currently used for login purposes only

        outSocket = self.outSocket()
        loginObject = RAProtocol.command(line)
        RAProtocol.sendMessage(loginObject, outSocket)
        #logger.write_line('Hidden: Making connection with remote server')
        message = RAProtocol.receiveMessage(outSocket)
        outSocket.close()

        ports = message
        print ports
        if ports in ['invalid', 'banned_name', "affiliation_get"]:
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "That login is invalid.  Again." )
            self.name = ""
            self.password = ""
        else:
            ports = ports.split()
            print ports
            self.iPort = int(ports[1])
            self.oPort = int(ports[0])
            print "oPort = %d, iPort = %d" % (self.oPort, self.iPort)
            self.loggedIn = True
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "You are now logged in...." )


    def shutDown(self):
        """function for proper shutdown of client & client/Server relations"""
        self.iThread.quit()
        self.iThread.deleteLater()


# class loginThread(QtCore.QThread):
#         """  Goes through the login process in the Gui Window """
#         def __init__(self, parent=None):
#             super(loginThread, self).__init__(parent)
#             print "arrived at login init"
#             self.loggedin = False
#
#         def run(self):
#
#             #self.start()
#             while self.loggedin == False:
#                 form.mainDisplay.append('Please enter your User Name. Or type "new" to create a new player')
#                 playerName =  form.outQueue.get()
#                 print playerName
#                 if playerName in ["n", "N", "new", "New", "NEW"]:
#                     # create a new player
#                     break
#                 form.mainDisplay.append('Please Enter Your Password')
#                 password = form.outQueue.get()
#                 print password

                #
                # loginLine= playerName, password
                # ports = connect_to_server(loginLine)
                #
                # if ports in ['invalid', 'banned_player', 'affiliation_get']:
                #     _In_Queue.put('That player/password is invalid or on the banned list.  Please try again.')
                # else:
                #     return ports





class inThread(QtCore.QThread):
    """ Primary thread listens for incoming messages, gets message and puts them
     on the inQueue to be processed by the main app.
    """

    def __init__(self, parent=None):
        super(inThread, self).__init__(parent)
        host = host.localHost
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.start()
        print "IN THREAD STARTED"

    def run(self):
        # Establish Socket & Listen
        print "i am here"

        self.sock.listen(2)
        while 1:
            #  Accept Connection from server
            print "I am here 2"
            conn, addr = self.sock.accept()
            print "I am here 3"
            connStream = ssl.wrap_socket(self.conn, certfile = 'cert.pem', server_side = True)
            message = RAProtocol.receiveMessage(conn)
            self.emit(QtCore.SIGNAL("connReceived(QObject)"), message)

            #exec()  # runs thread in it's own proper QEvent Loop allowing proper shutdown

# class outThread(QtCore.QThread):
#     def __init__(self, parent=None):
#         super(outThread, self).__init__(parent)




app = QtGui.QApplication(sys.argv)
form = MainDialog()
form.show()
app.exec_()
