__author__ = 'AYeager'

from PyQt4 import QtGui, QtCore, QtNetwork
import socket, ssl, sys, time, winsound
import RenA # this is the actual visual setup file
import Q2logging
import RAProtocol  # custom message packaging & sending


_Local_Host = socket.gethostname()
_Local_Host = socket.gethostbyname(_Local_Host)# replace with actual host address
_Server_Host = socket.gethostname() #'54.244.118.196' # replace with actual server address
_Login_Port = 60005


class MainDialog(QtGui.QDialog, RenA.Ui_mainDialog):
    """main GUI object"""

    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        self.log = Q2logging.out_file_instance('logs/GuiClient/PreLogins/')
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
        self.pingTimer = QtCore.QTimer() # Timer loop for sending stay alive pings

        self.oldStyle = True # Used to accommodate String/Tuple message format and message object formats
        self.setupUi(self) # Sets up Visual aspect of the Gui
        self.appendArt()
        self.iThread = inThread(self.iPort, self.localHost, self.log) #instantiate the in thread for establishing SIGNAL connections

        # Connections/Signals Main Object
        self.connect(self.pingTimer, QtCore.SIGNAL("timeout()"), self.pingServer)
        self.connect(self, QtCore.SIGNAL("mainDisplay(QString)"), self.appendDisplay, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("inputBox(QObject)"), self.fillTabs, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("artBox(QObject)"), self.appendArt, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("statusBox(QObject)"), self.appendStatus, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("playSound(QObject)"), self.playSound, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("readySend(QString)"), self.sendMessage, QtCore.Qt.DirectConnection)
        self.connect(self, QtCore.SIGNAL("sendOld"), self.sendMessage, QtCore.Qt.DirectConnection)
        #self.connect(self, QtCore.SIGNAL("readySend(QString)"), self.sendMessage, QtCore.Qt.DirectConnection)
        self.inputBox.returnPressed.connect(self.getUserInput)
        # Signal Connection for InThread
        self.connect(self.iThread, QtCore.SIGNAL("messageReceived(QString)"),  self.handleMessageReceived, QtCore.Qt.DirectConnection)

        self.mainDisplay.append('\n'*25+" "*10+'Welcome to the Ren Adventure!!'+'\n'*15)
        self.inputBox.setFocus()
        self.log.write_line('Main Gui object setup complete')
        self.main()

    def main(self):
        # this must be here to initiate Player interaction and properly activate the objects event loop
        self.emit(QtCore.SIGNAL("mainDisplay(QString)"), 'Enter User Name')
        self.log.write_line('Display initial prompt for game beginning.  "Enter user name"')

    def outSocket(self):
        # Sets up ssl connection to server on appropriate port.
        if self.loggedIn == False:
            port = self.lPort # login port
            self.log.write_line('Out socket being established with login port %s.' % str(self.lPort))
        else:
            port = self.oPort # out port set when log in is successful
            self.log.write_line('Out socket being established with out port %s.' % str(self.oPort))
        # Establish socket & connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem')
        ssl_sock.connect((_Server_Host, port))
        self.log.write_line('SSL socket created & connected')
        return ssl_sock

    def handleMessageReceived(self, message):
        #  Message router for incoming messages from the server.

        if self.oldStyle == True:
            if type(message) == 'tuple':  #  Message is tuple during standard game play
                self.log.write_line('message received was a tuple' + str(message))
                message = message[1]

            if '_play_' in message:  # Message for sound is simple string with tag
                self.log.write_line('message received was sound type %s' % message)
                sound = str(message).split()
                sound = sound[1]
                self.playSound(sound)
                message = "" #  makes item not append to screen

            else:  # messages during login and before entering room are simple strings
                self.log.write_line('message is simple string = %s' % str(message))
                self.emit(QtCore.SIGNAL("mainDisplay(QString)"), message )

        else:  #  message is an object type with attributes
            self.log.write_line('message is message object')
            if hasattr(message, "tags"):
                if "mainDisplay" in message.tags:
                    self.log.write_line('body = %s' & str(message.body))
                    self.emit(QtCore.SIGNAL("mainDisplay(QString)"), message.body )
                if "inputBox" in message.tags:
                    self.log.write_line('tabs = %s' % str(message.tabs))
                    self.emit(QtCore.SIGNAL("inputBox(RAProtocol.command)"), message.tabs)
                if "artBox" in message.tags:
                    self.log.write_line('art filename = %s' % str(message.art))
                    self.emit(QtCore.SIGNAL("artBox(QString)"), message.art)
                if "statusBox" in message.tags:
                    self.log.write_line('status = %s' % str(message.status))
                    self.emit(QtCore.SIGNAL("statusBox(QString)"), message.status)
                if "playSound" in message.tags:
                    self.log.write_line('sound file = %s' % str(message.sound))
                    self.emit(QtCore.SIGNAL("playSound"), message.sound)
                # if "login" in message.tags:
                #     if message.body == "accepted":
                #         self.loggedIn = True
                #     else:
                #         self.emit(QtCore.SIGNAL("mainDisplay(QString)"), 'Log-in failed.\nEnter User Name.')

    def appendDisplay(self, message):

        if message != "":
            self.mainDisplay.append("")
            self.mainDisplay.append(message)
            self.log.write_line('"%s" written to main Display.' % message )
            self.mainDisplay.moveCursor(QtGui.QTextCursor.End)
            self.inputBox.setFocus()

    def fillTabs(self):
        pass

    def appendStatus(self, message):
        pass

    def appendArt(self):

        self.artBox.clear()
        file = open('ASCII_art/Kanye1020.txt')
        #self.log.write_line('file for ascci Art printing = %s' % str(file))
        picString= ""
        for line in file:
            picString = line.strip()
            self.artBox.append(picString)
        self.log.write_line('art written to art display')

    def playSound(self, sound):

        path = 'sounds/%s.wav' % sound
        winsound.PlaySound(path, winsound.SND_FILENAME)
        self.log.write_line('sound played = %s' % str(sound))

    def getUserInput(self):
        """Captures and distributes User input from inputBox"""
        line = self.inputBox.displayText()
        self.log.write_line('user input captured = "%s"' % line)

        if line != "":
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), line )
            self.inputBox.clear()
            self.inputBox.setFocus()
            if self.loggedIn == False:
               self.login(line)
               self.log.write_line('sent to login function')
            else:
                if self.oldStyle == True:
                    message = str(line)
                    self.log.write_line('message format simple string')
                    self.emit(QtCore.SIGNAL("readySend(QString)"), message)

                else:
                    message = RAProtocol.QtCommand(name= str(self.name), body=str(line))
                    self.log.write_line('message format = object')



    def sendMessage(self, message):

        message = str(message)
        #message = pickle.loads(message)
        outSocket = self.outSocket()
        if self.oldStyle == False:
            # convert message object from QObject to regular object so RAP can handle properly
            message = RAProtocol.command(name= self.name, body=message)
            self.log.write_line('message packaged as object')
        RAProtocol.sendMessage(message, outSocket)

        outSocket.close()
        self.log.write_line('message sent socket closed')
        #self.pingTimer.start(4000)

    def pingServer(self):

        if self.oldStyle == True:
            message = '_ping_'
        else:
            message = '_ping_'
        outSocket= self.outSocket()
        RAProtocol.sendMessage(message, outSocket)
        outSocket.close()
        self.log.write_line('server pinged, keep alive')
        self.pingTimer.start(10000)

    def login(self, line):
         if self.name == "":
            self.name= line
            self.log.write_line('name captured = %s' % str(self.name))
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "Enter Password" )
         else:
            self.password = line
            self.log.write_line('password captured = %s' % str(self.password))
            if self.oldStyle == True:
                loginMessage = str(self.name + ' ' + self.password)
                self.log.write_line('login string = "%s"' % loginMessage)
            else:
                loginMessage = RAProtocol.command(tags=['login'], body= str(self.name + " " + self.password))
                self.log.write_line('login object created.')
            #self.emit(QtCore.SIGNAL("readySend(QObject)"), loginMessage)  #  Will likely be used in single port build
            self.connect_to_server(loginMessage)


    def connect_to_server(self, line):  #  currently used for login purposes only

        outSocket = self.outSocket()

        RAProtocol.sendMessage(line, outSocket)
        self.log.write_line('login message sent to server awaiting response')
        message = RAProtocol.receiveMessage(outSocket)  #return message from server validating login
        self.log.write_line('response recieved = %s' % str(message))
        outSocket.close()
        self.log.write_line('login socket closed.')

        ports = message
        if ports in ['invalid', 'banned_name', "affiliation_get"]: # login fails
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "That login is invalid.  Try Again." )
            self.name = ""
            self.password = ""
            self.log.write_line('login attempt invalid.  Reset Name and Password')
        else:  #logIn accepted process
            self.log.write_line('Login Valid changing login file to %s' % str(self.name))
            self.log = Q2logging.out_file_instance('logs/GuiClient/PlayLogs/%s' % str(self.name))
            ports = ports.split()
            self.iPort = int(ports[1])
            self.oPort = int(ports[0])
            self.log.write_line('in/out ports saved in = %d, out = %d' % (self.iPort, self.oPort))
            # set port and host for In thread... Start thread & start ping timer
            self.iThread.port = self.iPort
            self.iThread.host = self.localHost
            self.log.write_line('inThread atributes changed to inPort & localHost')
            self.iThread.start()
            self.pingTimer.start(10000)
            #  Login True for proper input box operation from this point forward.  Emit to print to display.
            self.loggedIn = True
            self.log.write_line('thread started, Ping timer Started')
            self.emit(QtCore.SIGNAL("mainDisplay(QString)"), "You are now logged in...." )


    def shutDown(self):
        """function for proper shutdown of client & client/Server relations"""
        self.log.write_line('shutdown function started')
        self.iThread.quit()
        self.iThread.deleteLater()
        self.log.write_line('shutdown successful')


class inThread(QtCore.QThread):
    """ Primary thread listens for incoming messages, gets message and puts them
     on the inQueue to be processed by the main app.
    """

    def __init__(self, port, host, log, parent=None):
        super(inThread, self).__init__(parent)
        self.log = log
        self.host = host
        self.port = port
        self.log.write_line('inThread instantiated')

    def run(self):
        self.log.write_line('inThread started')
        self.iSocket = self.inSocket()
        self.iSocket.listen(4)
        self.log.write_line('InSocket created, bound and listening port = %d, host = %s' % (self.port, str(self.host)))
        while 1:
            #  Accept Connection from server
            conn, addr = self.iSocket.accept()
            message = RAProtocol.receiveMessage(conn)
            self.log.write_line('message recieved on inThread = %s' % str(message))
            self.emit(QtCore.SIGNAL("messageReceived(QString)"), message)

    def inSocket(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem')
        return ssl_sock

class soundThread(QtCore.QThread):
    # Not used to play sound at this time done within Gui threads.  Leaving in code as it may need to be used at a later date.
    def __init__(self, sound, log, parent=None):
        super(soundThread, self).__init__(parent)
        self.sound = sound
        self.log = log
        self.log.write_line('sound thread initiated')

    def run(self):

        path = 'sounds/%s.wav' % self.sound
        winsound.PlaySound(path, winsound.SND_FILENAME)
        time.sleep(1)
        #self.quit()
        self.deleteLater()
        self.log.write_line('sound played, pause waited exiting thread')

app = QtGui.QApplication(sys.argv)
form = MainDialog()
form.show()
app.exec_()
