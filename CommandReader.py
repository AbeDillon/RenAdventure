__author__ = 'ADillon'

import threading
import Queue

_globalVerbs = []
_globalNouns = []

_TranslateCommand = {}
_TranslateVerb = {}
_TranslateNoun = {}

class CommandReader(threading.Thread):
    """
    This thread reads commands from a command-queue and either routes them or processes them accordingly.
    The manner in-which commands are processed is specified by the subclass or something IDK...
    """

    def __init__(self, messageQ, commandQ, killFlag, killLock):
        # superclass constructor
        threading.Thread.__init__(self)
        # input and output queues
        self.messageQ = messageQ
        self.commandQ = commandQ
        # termination signal
        self.killFlag = killFlag
        self.killLock = killLock
        # routing table
        self.route = dict()

    def run(self):
        # INITIALIZE

        # set-up main loop
        with self.killLock:
            done = self.killFlag

        # MAIN LOOP
        while done:
            # listen for new command
            command = self.commandQ.get()

            # unpack command
            name = command.name
            tags = command.tags
            text = command.text

            # check routing table
            route = self.route.get(name, False)
            if route:
                route.put(command)
            else:
                # if the command isn't routed, it is processed
                self.checkTags()


            # check termination flag
            with self.killLock:
                done = self.killFlag

        # TEAR DOWN
        return

    def checkTags(self):
        """

        """
        pass