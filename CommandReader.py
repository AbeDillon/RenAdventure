__author__ = 'ADillon'

from threading import Thread, RLock
from Queue import Queue
from RAProtocol import command


class CommandReader(Thread):
    """
    This thread reads commands from a command-queue and either routes them or processes them accordingly.
    The manner in-which commands are processed is specified by the subclass which should overwrite the
    processTags() and processCommand() functions.
    """

    def __init__(self, inQ=Queue(), outQ=Queue()):
        # superclass constructor
        Thread.__init__(self)
        # input and output queues
        self.inQ = inQ
        self.outQ = outQ
        # termination signal
        self.done = False
        # routing table
        self.routeTable = dict()

    def run(self):
        # MAIN LOOP
        while not self.done:
            # listen for new message
            cmd = self.inQ.get()

            # route message
            cmd = self.route(cmd)

            # handle tags
            if cmd != None:
                cmd = self.processTags(cmd)
                pass

            # execute command
            if cmd != None:
                self.processCommand(cmd)
                pass

        # kill sub-threads
        kill = command("", ["kill thread"], "")
        for Q in self.routeTable:
            Q.put(kill)

        return

    def route(self, cmd):
        """
        Route commands to their correct destination
        """
        name = cmd.name
        # check routing table
        destination = self.routeTable.get(name, False)
        if destination:
            destination.put(cmd)
            return None
        else:
            return cmd

    def processTags(self, cmd):
        """
        This function should be overwritten by the sub-class that inherits from commandReader
        """
        tags = cmd.tags
        if "kill thread" in tags:
            self.done = True
            return None
        if "thread done" in tags:
            name = cmd.body
            if name in self.routeTable:
                self.routeTable.pop(name)
                return None
            else:
                print "ERROR: The name; " + name + ", was not found in the route table."
                return None

        return cmd

    def processCommand(self, cmd):
        """
        This function should be overwritten by the sub-class that inherits from commandReader
        """
        pass

_globalVerbs = []
_globalNouns = []

_TranslateCommand = {}
_TranslateVerb = {}
_TranslateNoun = {}