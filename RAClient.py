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
        self.ping_timer = QtCore.QTimer()

        self.oldStyle = True
        self.setupUi(self)

        # build input and output objects
        self.inQueue = Queue.Queue()
        self.outQueue = Queue.Queue()

        # Local Server Build
        self.iThread = inThread(self.iPort, self.localHost)

        # Connections/Signals
        self.connect(self.ping_timer, QtCore.SIGNAL("timeout(QString)"), self.pingServer)
        self.connect(self, QtCore.SIGNAL("mainDisplay(QString)"), self.appendDisplay, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("inputBox(QObject)"), self.fillTabs, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("artBox(QObject)"), self.appendArt, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("statusBox(QObject)"), self.appendStatus, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("playSound(QObject)"), self.playSound, QtCore.Qt.DirectConnection)
        #self.connect(self, QtCore.SIGNAL("readySend(QString)"), self.sendMessage, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("sendOld"), self.sendMessage, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("readySend(QString)"), self.sendMessage, QtCore.Qt.DirectConnection)
        self.inputBox.returnPressed.connect(self.getUserInput)
        self.connect(self.iThread, QtCore.SIGNAL("messageReceived(QString)"),  self.handleMessageReceived, QtCore.Qt.DirectConnection)

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

    def handleMessageReceived(self, message):

        if self.oldStyle == True:
            if type(message) == 'tuple':
                message = message[1]
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), message )
        else:
            if hasattr(message, "tags"):
                if "mainDisplay" in message.tags:
                    self.emit(QtCore.SIGNAL("mainDisplay(QString)"), message.body )
                if "inputBox" in message.tags:
                    self.emit(QtCore.SIGNAL("inputBox(RAProtocol.command)"), message)
                if "artBox" in message.tags:
                    self.emit(QtCore.SIGNAL("artBox(QString)"), message.art)
                if "statusBox" in message.tags:
                    self.emit(QtCore.SIGNAL("statusBox(QString)"), message.status)
                if "playSound" in message.tags:
                    self.emit(QtCore.SIGNAL("playSound"), message.sound)
                # if "login" in message.tags:
                #     if message.body == "accepted":
                #         self.loggedIn = True
                #     else:
                #         self.emit(QtCore.SIGNAL("mainDisplay(QString)"), 'Log-in failed.\nEnter User Name.')



    def main(self):

        self.emit(QtCore.SIGNAL("mainDisplay(QString)"), 'Enter User Name.')


    def appendDisplay(self, message):

        self.mainDisplay.append(message)
        self.mainDisplay.moveCursor(QtGui.QTextCursor.End)
        self.inputBox.setFocus()


    def fillTabs(self):
        pass

    def appendStatus(self, message):
        pass

    def appendArt(self, message):
        self.artBox.clear()
        self.artBox.append(message.art)

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
        #message = pickle.loads(message)
        outSocket = self.outSocket()
        if self.oldStyle == False:
            # convert message object from QObject to regular object so RAP can handle properly
            message = RAProtocol.command(message)
        RAProtocol.sendMessage(message, outSocket)
        outSocket.close()
        self.ping_timer.start(4000)

    def pingServer(self):

        if self.oldStyle == True:
            message = (str(self.name), '_Ping_', [])
        else:
            message = (str(self.name), '_Ping_', [])
        outSocket= self.outSocket()
        RAProtocol.sendMessage(message, outSocket)
        outSocket.close()
        self.ping_timer.start(4000)

    def login(self, line):
         if self.name == "":
            self.name= line
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "Enter Password" )
         else:
            self.password = line
            loginMessage = RAProtocol.QtCommand(tags=['login'], body= self.name + " " + self.password)
            #self.emit(QtCore.SIGNAL("readySend(QObject)"), loginMessage)  #  Will likely be used in single port build
            self.connect_to_server(loginMessage)


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
            self.iThread.port = self.iPort
            self.iThread.host = self.localHost
            self.iThread.start()
            self.ping_timer.start(4000)
            self.loggedIn = True
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "You are now logged in...." )


    def shutDown(self):
        """function for proper shutdown of client & client/Server relations"""
        self.iThread.quit()
        self.iThread.deleteLater()


class inThread(QtCore.QThread):
    """ Primary thread listens for incoming messages, gets message and puts them
     on the inQueue to be processed by the main app.
    """

    def __init__(self, port, host, parent=None):
        super(inThread, self).__init__(parent)

        self.host = host
        self.port = port
        print "IN THREAD STARTED"

    def run(self):

        self.iSocket = self.inSocket()
        self.iSocket.listen(4)
        while 1:
            #  Accept Connection from server
            conn, addr = self.iSocket.accept()
            message = RAProtocol.receiveMessage(conn)
            print "RECIEVED AT THREAD\n", message
            self.emit(QtCore.SIGNAL("messageReceived(QString)"), message)

    def inSocket(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem')
        return ssl_sock





app = QtGui.QApplication(sys.argv)
form = MainDialog()
form.show()
app.exec_()
