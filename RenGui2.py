__author__ = 'AYeager'
__author__ = 'ADillon, MNutter, AYeager'

from PyQt4 import QtGui, QtCore
import Queue, sys, time, msvcrt
import socket, ssl, string, winsound
import thread, threading
import RAProtocol, Q2logging
import RenUi_Form

#Define Logs
logger = Q2logging.out_file_instance('logs/client/RenClient')

#sockets
_Local_Host = socket.gethostname()
_Server_Host = socket.gethostname()
_Login_Port = 60005

_CMD_Queue = Queue.Queue()  # Global Command Queue for client input

_Quit = False
_Quit_Lock = threading.RLock()
_Sound_Playing = False

class RenConsole(QtGui.QDialog):

    def __init__(self, parent=None):
        super(RenConsole, self).__init__(parent)
        self.setWindowTitle("A Ren Adventure")
        self.setGeometry(200,50,640,480)

        self.loggedIn = False
        self.getAff = False
        self.playerName = ""
        self.password = ""

        #self.pallette = QtGui.QPalette("fg=green, bg = black")
        # Main Display area
        self.mainDisplay = QtGui.QTextEdit()
        self.mainDisplay.setAcceptRichText(False)
        self.mainDisplay.setAcceptDrops(False)
        self.mainDisplay.setFontFamily('consolas')

        # input area
        self.inputBox = QtGui.QLineEdit()
        self.inputBox.setFocus()
        #self.inputBox.setPalette(self.pallette)
        #self.connect(self.inputBox, QtCore.SIGNAL("returnPressed()"), self.sendInput )

        # Build Layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.mainDisplay)
        layout.addWidget(self.inputBox)
        self.setLayout(layout)

        self.inputBox.setFocus()
        self.mainDisplay.append('\n'*15 + 'Welcome to the Ren Adventure!')
        self.loggedIn = False
        self.playerName = ""
        self.password = ""

#  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def login():
    """  Goes through the login process in the Gui Window """
    #global _CMD_Queue

    console.mainDisplay.append('Welcome to the Ren Adventure!')
    while console.loggedIn == False:
        while console.playerName == "":
            _CMD_Queue.put('Please enter your User Name. Or type "new" to create a new player')
            # need to wait for response before prompting again
        if console.playerName == 'new':
            affDict = getAffiliation()
        while console.password == "":
            console.mainDisplay.append('Please enter your password.')
            # wait for response before prompting again
        # gather data and send to login
        loginString = console.playerName, console.password
        console.mainDisplay.append(loginString)
        ports = connect_to_server(loginString)
        if ports == 'invalid' or ports == 'banned_player':
            #  Not valid login reset variables and start over
            console.mainDisplay.append('Your player/password was invalid, banned, or not found try again.')
            console.playerName = ""
            console.password = ""


def getAffiliation():
    """used for getting new player affiliations"""
    console.getAff = True
    pList = ['Obama', 'Kanye', 'O''Rielly', 'Gottfreid', 'Burbiglia']
    ranks = [5,4,3,2,1]
    pRank = {'Obama':0, 'Kanye':0, 'ORielly':0, 'Gottfreid':0, 'Burbigilia':0}

    for person in pList:
        #console.maindisplay.
        pass

    return pRank

def connect_to_server(line):
    """
    uses login line to connect to server and validate login.
    returns ports of I/O Threads if Success or.....
    invalid, banned, affiliation_get

    """
    global _Server_Host
    global _Login_Port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(sock, certfile = 'cert.pem')
    ssl_sock.connect((_Server_Host, _Login_Port))

    RAProtocol.sendMessage(line, ssl_sock)
    logger.write_line('Hidden: Making connection with remote server')

    message = RAProtocol.receiveMessage(ssl_sock)

    ssl_sock.close()
    return message

def getMessage():
    if _CMD_Queue > 0:
        message = _CMD_Queue.get()
        console.mainDisplay.append(message)

def sendInput():

    line = console.inputBox.displayText()

    if line != "":
        ##handle input for Login function
        if console.loggedIn == False and console.getAff == False:
            if console.playerName == "":
                console.playerName = line
            if console.playerName != "" and console.password == "":
                console.password = line
            if console.playerName != "" and console.password != "":
                loginText = console.playerName, console.password
                # send to login thread
                # if success do this
                #elif fails
                    #previous login failed reset values for another attempt
                pass
        if console.getAff == True:
            pass
        else:
            try:
                _CMD_Queue.put(line)
                logger.write_line('Input from user: %s' % line)
            except:
                pass
    # Empty strings are ignored and cleared

    console.inputBox.clear()




if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    console = RenConsole()## Open GUI

    login()


    timer = QtCore.QTimer(console)
    timer.start(1000)

    #connections
    console.inputBox.returnPressed.connect(sendInput)
    console.mainDisplay.timeout.connect(getMessage)

    console.show()
    console.setFocus()
    console.inputBox.setFocus()
    #login()
    sys.exit(app.exec_())







