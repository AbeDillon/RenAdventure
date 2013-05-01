__author__ = 'AYeager'

from PyQt4 import QtGui, QtCore, QtNetwork
import socket, ssl
import sys
import RenA
import Queue
import RAProtocol

#address = QtNetwork.Q
_Local_Host = socket.gethostname()
_Local_Host = socket.gethostbyname(_Local_Host)# replace with actual host address
_Local_Host = QtNetwork.QHostAddress(_Local_Host)
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
        self.port = _Login_Port
        self.loggedIn = False
        self.nameGotten = False

        self.setupUi(self)

        # build input and output objects
        self.inQueue = Queue.Queue()
        self.outQueue = Queue.Queue()

        # Local Server Build
        self.initServer()

        # Connections/Signals
        self.connect(self, QtCore.SIGNAL("mainDisplay(QString)"), self.appendDisplay, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("inputBox(QObject)"), self.fillTabs, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("artBox(QObject)"), self.appendArt, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("statusBox(QObject)"), self.appendStatus, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("playSound(QObject)"), self.playSound, QtCore.Qt.DirectConnection)
        self.inputBox.returnPressed.connect(self.getUserInput)
        self.connect(self.tcpServer, QtCore.SIGNAL("newConnection()"), self.handleNewConnection)

        self.mainDisplay.append('\n'*25+" "*10+'Welcome to the Ren Adventure!!'+'\n'*15)
        self.inputBox.setFocus()
        self.main()

    def initServer(self):
        self.tcpServer = QtNetwork.QTcpServer()
        self.tcpServer.listen(self.localHost, self.port)


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

        #self.Login.start()

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
                if not self.nameGotten:

                    self.name= line
                    self.nameGotten=True
                    self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "Enter Password" )
                else:
                    self.password = line
                    loginMessage = RAProtocol.command(tags=['login'], body = self.name +"\n"+self.password)

    def sendMessage(self, message):
        outSocket = QtNetwork.QSslSocket


    def shutDown(self):
        """function for proper shutdown of client & client/Server relations"""
        self.iThread.quit()
        self.iThread.deleteLater()


class loginThread(QtCore.QThread):
        """  Goes through the login process in the Gui Window """
        def __init__(self, parent=None):
            super(loginThread, self).__init__(parent)
            print "arrived at login init"
            self.loggedin = False

        def run(self):

            #self.start()
            while self.loggedin == False:
                form.mainDisplay.append('Please enter your User Name. Or type "new" to create a new player')
                playerName =  form.outQueue.get()
                print playerName
                if playerName in ["n", "N", "new", "New", "NEW"]:
                    # create a new player
                    break
                form.mainDisplay.append('Please Enter Your Password')
                password = form.outQueue.get()
                print password

                #
                # loginLine= playerName, password
                # ports = connect_to_server(loginLine)
                #
                # if ports in ['invalid', 'banned_player', 'affiliation_get']:
                #     _In_Queue.put('That player/password is invalid or on the banned list.  Please try again.')
                # else:
                #     return ports





# class inThread(QtCore.QThread):
#     """ Primary thread listens for incoming messages, gets message and puts them
#      on the inQueue to be processed by the main app.
#     """
#
#     def __init__(self, localHost, port, parent=None):
#         super(inThread, self).__init__(parent)
#         self.host = localHost
#         self.port = port
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.bind((self.host, self.port))
#         self.start()
#         print "IN THREAD STARTED"
#
#     def run(self):
#         # Establish Socket & Listen
#         print "i am here"
#
#         self.sock.listen(2)
#         while 1:
#             #  Accept Connection from server
#             print "I am here 2"
#             conn, addr = self.sock.accept()
#             print "I am here 3"
#             connStream = ssl.wrap_socket(self.conn, certfile = 'cert.pem', server_side = True)
#             message = RAProtocol.receiveMessage(conn)
#             self.emit(QtCore.SIGNAL("connReceived(QObject)"), message)
#
#             #exec()  # runs thread in it's own proper QEvent Loop allowing proper shutdown

# class outThread(QtCore.QThread):
#     def __init__(self, parent=None):
#         super(outThread, self).__init__(parent)




app = QtGui.QApplication(sys.argv)
form = MainDialog()
form.show()
app.exec_()
