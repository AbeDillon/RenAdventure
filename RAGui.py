__author__ = 'AYeager'

from PyQt4 import QtGui, QtCore
import sys, threading, thread, Queue

_Out_Queue = Queue.Queue()
_In_Queue = Queue.Queue()



#+++++++++++++++++++++UI OBJECTS+++++++++++++++++++++++++++

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
        #self.inputBox.setPalette(self.pallette)
        #self.connect(self.inputBox, QtCore.SIGNAL("returnPressed()"), self.sendInput )

        # Build Layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.mainDisplay)
        layout.addWidget(self.inputBox)
        self.setLayout(layout)



#++++++++LOGIC OBJECTS+++++++++++++++++++++++++++++++
class InThread(threading.Thread):
    def __init__(self):
        pass

class OutThread(threading.Thread):
    def __init__(self):
        pass

#++++++++++++++FUNCTIONS/LOGIC+++++++++++++++++++++++


def login():
    """  Goes through the login process in the Gui Window """
    #global _CMD_Queue

    global _In_Queue
    global  _Out_Queue
    loggedin = False

    while not loggedin:
        _In_Queue.put('Please enter your User Name. Or type "new" to create a new player')
        playerName =  _Out_Queue.get()
        if playerName in ["n", "N", "new", "New", "NEW"]:
            # create a new player
            break
        _In_Queue.put('Please Enter Your Password')
        password = _Out_Queue.get()

        loginLine= playerName, password
        ports = connect_to_server(loginLine)

        if ports in ['invalid', 'banned_player', 'affiliation_get']:
            _In_Queue.put('That player/password is invalid or on the banned list.  Please try again.')
        else:
            pass



    # while console.loggedIn == False:

    #         # need to wait for response before prompting again
    #     if console.playerName == 'new':
    #         affDict = getAffiliation()
    #     while console.password == "":
    #         console.mainDisplay.append('Please enter your password.')
    #         # wait for response before prompting again
    #     # gather data and send to login
    #     loginString = console.playerName, console.password
    #     console.mainDisplay.append(loginString)
    #     ports = connect_to_server(loginString)
    #     if ports == 'invalid' or ports == 'banned_player':
    #         #  Not valid login reset variables and start over
    #         console.mainDisplay.append('Your player/password was invalid, banned, or not found try again.')
    #         console.playerName = ""
    #         console.password = ""

def connect_to_server(line):
    """

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







def playerInput():
    #  Function receives player input from console.inputBox
    global _Out_Queue

    line = console.inputBox.displayText()
    _In_Queue.put(line)
    _Out_Queue.put(line)
    console.inputBox.clear()


def printMessage():
    #  Function to print message received from Server
    global _In_Queue

    if not _In_Queue.empty():
        message = _In_Queue.get()
        console.mainDisplay.append(message)
    else:
        pass















if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    console = RenConsole()

    timer = QtCore.QTimer(console)
    timer.start(35)
    console.mainDisplay.append('\n'*15+'Welcome to the Ren Adventure!!')
    login()
    timer.timeout.connect(printMessage)

    console.inputBox.returnPressed.connect(playerInput)

    console.show()
    console.inputBox.setFocus()

    sys.exit(app.exec_())


