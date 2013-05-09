__author__ = 'AYeager'

import BuilderHelper
import threading
import Q2logging
import engine_classes


import engine_classes
import BuilderHelper as bh

"""  Builder will be implemented in a Thread from the server/engine at a later time. """

class builder():
    def __init__(self, type=None):

        self.type = type

        # Player/Builder definable attributes and the function for defining them in BuilderHelper.py
        # dontBreak CALLS MUST DISAPPEAR!!!!!!!  IE I need to build the proper functions to replace them....

        self.dispatcher = { 'name':bh.name, 'desc':bh.description, 'inspect_desc':bh.inspect_description, 'textID':bh.textID,
                    'scripts':bh.dontBreak, 'portable':bh.getBool, 'hidden':bh.getBool,
                    'container':bh.getBool, 'locked':bh.getBool, 'key':bh.dontBreak,
                    'items':bh.dontBreak, 'editors':bh.dontBreak, 'direction':bh.dontBreak,
                    'coords':bh.dontBreak, 'portals':bh.dontBreak}
        # List of editable Attributes of objects.  Using this list will order flow through object attribute definition
        self.editList = ['name', 'desc', 'inspect_desc', 'textID', 'direction', 'hidden', 'portable', 'container', 'locked', 'key',
                    'items', 'scripts' ]

    #  I want this in a def run(self):  But it did not seem to work for me....??!!?!!??
        if self.type == "item":
            itemObj = engine_classes.Item()
            self.buildObject(itemObj)
        if self.type == "npc":
            npcObj = engine_classes.NPC()
            self.buildObject(npcObj)


    def buildObject(self, obj):

        for attr in self.editList:

            if attr in dir(obj):
                self.attr = attr
                newValue = self.dispatcher[attr](self)
                setattr(obj, attr, newValue)
                print getattr(obj, attr)

        #  Review Object

        #  Pack & Save Object


if __name__ == '__main__':

    builder(type='item')