__author__ = 'ADillon, MNutter, AYeager'

from PyQt4 import QtGui, QtCore
import Queue, sys, time, msvcrt
import socket, ssl, string, winsound
import thread, threading
import RAProtocol, Q2logging

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
        self.playerName = str
        self.password = str

        # Main Display area
        self.mainDisplay = QtGui.QTextEdit()
        self.mainDisplay.setAcceptRichText(False)
        self.mainDisplay.setAcceptDrops(False)
        self.mainDisplay.setFontFamily('consolas')

        # input area
        self.inputBox = QtGui.QLineEdit()
        self.connect(self.inputBox, QtCore.SIGNAL("returnPressed()"), self.sendInput )

        # Build Layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.mainDisplay)
        layout.addWidget(self.inputBox)
        self.setLayout(layout)

        self.inputBox.setFocus()
        self.mainDisplay.append('\n'*15 + 'Welcome to the Ren Adventure!')



    def run(self):

        self.Login()


    def Login(self):
        """  Goes through the login process in the Gui Window """
        #global _CMD_Queue

        self.mainDisplay.append('Welcome to the Ren Adventure!')
        while self.loggedIn == False:
            while self.playerName == "":
                self.mainDisplay.append('Please enter your User Name.')
                # need to wait for response before prompting again
            while self.password == "":
                self.mainDisplay.append('Please enter your password.')
                # wait for response before prompting again
            # gather data and send to login
                loginString = self.playerName, self.password
                self.mainDisplay.append(loginString)

    def sendInput(self):

        line = self.inputBox.displayText()

        if line != "":
            ##handle input for Login function
            if self.loggedIn == False:
                if self.playerName == "":
                    self.playerName = line
                if self.playerName != "" and self.password == "":
                    self.password = line
                if self.playerName != "" and self.password != "":
                    #create string and send to login thread
                    # if success do this
                    #elif fails
                        #previous login failed reset values for another attempt
                    pass
            else:
                try:
                    _CMD_Queue.put(line)
                    logger.write_line('Input from user: %s' % line)
                except:
                    pass
        # Empty strings are ignored and cleared

        self.inputBox.clear()




app= QtGui.QApplication(sys.argv)
console = RenConsole()## Open GUI
console.show()
console.setFocus()
app.exec_()







