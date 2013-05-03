__author__ = 'AYeager'

from PyQt4 import QtGui, QtCore
import sys, Queue
import socket, RAProtocol, ssl
import Q2logging
import RenA_UI

logger = Q2logging.out_file_instance('logs/client/RenClient')

_Local_Host = socket.gethostname() # replace with actual host address
_Server_Host = socket.gethostname() #'54.244.118.196' # replace with actual server address
_Login_Port = 60005

_Out_Queue = Queue.Queue()
_In_Queue = Queue.Queue()



#+++++++++++++++++++++UI OBJECT+++++++++++++++++++++++++++
class renConsole(QtGui.QMainWindow, RenA.Ui_MainWindow):
    def __int__(self, parent=None):
        super(renConsole, self).__init__(parent)
        self.setupUi()



#++++++++LOGIC OBJECTS+++++++++++++++++++++++++++++++
class inThread(QtCore.QThread):
    def __init__(self, parent=None):
        super(inThread, self).__init__(parent)

    def run(self):
        pass

class OutThread(QtCore.QThread):
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
            return ports



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







def main():


    ports = login()
    #console.mainDisplay.append(str(ports))






if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    console = renConsole()
    #console.self.mainDisplay.append('\n'*15+'Welcome to the Ren Adventure!!'+ '\n'*15)
    timer = QtCore.QTimer(console)
    timer.start(35)
    #console.mainDisplay.append('blah blah')
    #Signal Connections
    timer.timeout.connect(printMessage)
    #console.inputBox.returnPressed.connect(playerInput)

    console.show()
    #console.self.inputBox.setFocus()
    #while 1:
        #main()

    sys.exit(app.exec_())


