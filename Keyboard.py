__author__ = 'ADillon'

import Queue
import threading
import msvcrt
import string
import time

class KBListener(threading.Thread):
    """
    This thread reeds input from the keyboard
    """

    def __init__(self, inQ, outQ, displayLine, displayLineLock, killFlag, killLock):
        # Superclass constructor
        threading.Thread.__init__(self)

        self.inQ = inQ
        self.outQ = outQ

        self.displayLine = displayLine
        self.displayLineLock = displayLineLock

        # termination signal
        self.killFlag = killFlag
        self.killLock = killLock

        self.leftLine = ""
        self.rightLine = ""

        self.insert = False

        self.tabOptions = Queue.Queue()

        self.history = []
        self.history_index = 0

    def run(self):
        # INITIALIZE
        specialChars = [0, 224]

        # set-up main loop
        with self.killLock:
            done = self.killFlag

        # MAIN LOOP
        while not done:

            char = msvcrt.getch()
            code = ord(char)

            if code in specialChars: # Special Key
                self.specialKey()
            elif char == "\r":      # Enter
                self.newLine()
            elif char == "\x08":    # Backspace
                self.backspace()
            elif char in string.printable[0:-5]:
                self.addChar(char)

            # update display line
            line = self.leftLine + self.rightLine
            with self.displayLineLock:
                self.displayLine = line

            time.sleep(0.01)
            # check termination flag
            with self.killLock:
                done = self.killFlag

        # TEAR DOWN
        return

    def specialKey(self):
        # get second half of key code
        char = msvcrt.getch()
        code = ord(char)

        if code == 72:      # up arrow
            self.upArrow()
        elif code == 80:    # down arrow
            self.downArrow()
        elif code == 75:    # left arrow
            self.leftArrow()
        elif code == 77:    # right arrow
            self.rightArrow()
        elif code == 82:    # insert
            self.insert = not self.insert
        elif code == 83:    # delete
            self.delete()
        elif code == 73:    # page up
            self.pageUp()
        elif code == 81:    # page down
            self.pageDown()
        elif code == 71:    # home key
            self.homeKey()
        elif code == 79:    # end key
            self.endKey()

    def newLine(self):
        # Add command to the output Queue and command history
        line = self.leftLine + self.rightLine
        message = (line, [])
        self.outQ.put(message)
        # update history
        self.history.append(line)
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        self.history_index = len(self.history) - 1

        # re-initialize
        self.leftLine = ""
        self.rightLine = ""
        self.tabOptions = Queue.Queue()

    def backspace(self):
        # remove a character to the left of the cursor
        if len(self.leftLine) > 0:
            # remove a character from the string
            self.leftLine = self.leftLine[:-1]
            # flush tab options
            self.tabOptions = Queue.Queue()

    def addChar(self, char):
        # add a character
        self.leftLine += char
        if self.insert and (len(self.rightLine) > 0):
            self.rightLine = self.rightLine[1:]

        # flush tab options
        self.tabOptions = Queue.Queue()

    def tab(self):
        # send a tab-complete message or cycle through tab-complete options
        if self.tabOptions.empty():
            # send a request for a tab-completion list
            message = (self.leftLine, ['tab-complete'])
            self.outQ.put(message)
            # listen for a response
            options = self.inQ.get()
            if options != None:
                # fill the FIFO Queue with response
                for option in options:
                    self.tabOptions.put(option)
                # begin cycling through tab-options
                self.tab()
        else:
            self.leftLine = self.tabOptions.get()
            self.tabOptions.put(self.leftLine)
            if self.insert:
                # overwrite the end of the line
                self.rightLine = ""

    def upArrow(self):
        # step back through command history
        idx = self.history_index
        if idx > 0:
            idx -= 1
            self.history_index = idx
            self.leftLine = self.history[idx]
            self.rightLine = ""
            # flush tab options
            self.tabOptions = Queue.Queue()

    def downArrow(self):
        # step forward through command history
        idx = self.history_index
        idx += 1
        if idx < len(self.history):
            self.history_index = idx
            self.leftLine = self.history[idx]
            self.rightLine = ""
            # flush tab options
            self.tabOptions = Queue.Queue()

    def leftArrow(self):
        # move cursor back one space
        if len(self.leftLine) > 0:
            # move cursor left
            self.rightLine = self.leftLine[-1] + self.rightLine
            self.leftLine = self.leftLine[:-1]
            # flush tab options
            self.tabOptions = Queue.Queue()

    def rightArrow(self):
        # move cursor forward one space
        if len(self.rightLine) > 0:
            # move cursor right
            self.leftLine += self.rightLine[0]
            self.rightLine = self.rightLine[1:]
            # flush tab options
            self.tabOptions = Queue.Queue()

    def delete(self):
        # remove a character to the right of the cursor
        if len(self.rightLine) > 0:
            self.rightLine = self.rightLine[1:]

    def pageUp(self):
        # send a message to the display to scroll back through its history buffer
        pass

    def pageDown(self):
        # send a message to the display to scroll forward through its history buffer
        pass

    def homeKey(self):
        # send a message to the display to scroll to the beginning of its history buffer
        pass

    def endKey(self):
        # send a message to the display to scroll to the end of its history buffer
        pass


def KBcode():
    """
    prints the keyboard code for each key typed (except backspace (ord 8) which breaks out of the function)
    """
    a = 0
    while a != 8:
        char = msvcrt.getch()
        a = ord(char)
        if a in [000, 224]:
            char2 = msvcrt.getch()
            b = ord(char2)
            print str(a) + ":" + str(b)
        else:
            print str(a)

# horz = chr(205) # horizontal
# vert = chr(186) # vertical
# topl = chr(201) # top-left corner
# topr = chr(187) # top-right corner
# botl = chr(200) # bottom-left corner
# botr = chr(188) # bottom-right corner
# nort = chr(202) # North T-intersection
# sout = chr(203) # South T-intersection
# east = chr(204) # East T-intersection
# west = chr(185) # West T-intersection
# cros = chr(206) # Cross intersection
# empt = " "      # Space
# newl = "\n"     # New-line