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

#++++++++LOGIC OBJECTS+++++++++++++++++++++++++++++++
class InThread(threading.Thread):
    def __init__(self):
        pass

class OutThread(threading.Thread):
    def __init__(self):
        pass

#++++++++++++++FUNCTIONS/LOGIC+++++++++++++++++++++++


def login():
    global _In_Queue

    _In_Queue.put('Please enter your Player Name')

    pass

def playerInput():
    #  Function receives player input from console.inputBox
    global _Out_Queue

    line = console.inputBox.displayText()
    _Out_Queue.put(line)
    _In_Queue.put(line)
    console.inputBox.clear()

def playerInputLogin():
    pass

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
    console.mainDisplay.append('\n'*15+'Welcome to the Ren Adventure.')

    timer.timeout.connect(printMessage)

    console.inputBox.returnPressed.connect(playerInput)

    console.show()
    console.inputBox.setFocus()

    sys.exit(app.exec_())


