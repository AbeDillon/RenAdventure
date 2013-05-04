
"""
Work in progress.  main() is there to test dbManager.
"""
import sqlite3
import datetime
import os


class dbManager(object):
    #  Creates the necessary file and folder to put the db in.  A single file can hold multiple tables but it
    # is probably wise to not put more than one in a file at a time.
    def __init__(self, folder="database", dbName="Ren.db"):
        self.folder = folder
        self.dbName = dbName
        directories = os.listdir(os.getcwd())
        if self.folder not in directories:
            os.mkdir(self.folder)

        if self.dbName not in os.listdir(os.getcwd() + "\\" + self.folder):
            # create the DB file
            fin = open(os.getcwd() + "\\" + self.folder + "\\" + self.dbName, 'w')
            fin.close()
            # open the DB
            self.db = sqlite3.connect(os.getcwd() + "\\" + self.folder + "\\" + self.dbName)
            self.query = self.db.cursor()
            self.createTable()
        else:
            #  This does not check the contents of the file, only the file name.
            self.db = sqlite3.connect(os.getcwd() + "\\" + self.folder + "\\" + self.dbName)
            self.query = self.db.cursor()

    def createTable(self):
        #  The PRIMARY KEY command automatically assigns a unique number (auto-increment from 1) to the entry so we
        #  don't have to.  Do not try to assign this number.
        self.query.execute('''CREATE TABLE globalObject
        (uniqueId INTEGER PRIMARY KEY, dateAdded TEXT, name TEXT, objectType TEXT, creator TEXT, dateCreated TEXT, dateModified TEXT,
        dateUsed TEXT, upVotes INTEGER, downVotes INTEGER)''')
    
    def addObject(self, dateAdded, name, objectType, creator, dateCreated, dateModified, dateUsed, upVotes, downVotes):
        self.query.execute('''INSERT INTO globalObject(dateAdded, name, objectType, creator, dateCreated, dateModified, dateUsed, upVotes, downVotes)
        VALUES (?,?,?,?,?,?,?,?,?)''', (dateAdded, name, objectType, creator, dateCreated, dateModified, dateUsed, upVotes, downVotes))

        ##  TODO -  Items/Ideas that could be done

        # We need a XML field where objects can be packed to and unpacked from an XML file that would contain all its attributes.
        # this currently only contains place for information regarding objects not any storage of the actual object.  We need this to be
        # a toy box where objects can be put in for storage and taken out to be played with at a later time.

        # Also need a field for users with editing privileges field so we know who has permission to edit objects before they are
        # "taken out" (unpacked from xml) to be edited.

def main():

    dbm = dbManager()
    stamp = datetime.datetime.now()

    #  Sample variables
    upVotes1 = 1
    upVotes12 = 12
    upVotes14 = 14
    upVotes4 = 4
    
    downVotes14 = 14
    downVotes140 = 140
    downVotes7 = 7
    downVotes20 = 20

    #  sqlite allows duplicate values, i.e. Fancy Door is used twice here but each gets its own primary key.
    dbm.addObject(stamp, 'Fancy Door', 'portal', 'Joe Bob', '4/20/13', '4/22/13', '4/24/13', upVotes1, downVotes14)
    dbm.addObject(stamp, 'Fancy chest', 'container', 'Billy Bob', '4/2/13', '4/4/13', '4/4/13', upVotes12, downVotes140)
    dbm.addObject(stamp, 'Fancy Sword', 'object', 'Darlene', '4/21/13', '4/22/13', '4/30/13', upVotes14, downVotes7)
    dbm.addObject(stamp, 'Fancy Potion', 'object', 'Marlene', '4/25/13', '4/25/13', '4/25/13', upVotes4, downVotes20)
    dbm.addObject(stamp, 'Fancy Door', 'portal', 'Ellie Mae', '4/2/13', '4/5/13', '4/24/13', upVotes12, downVotes14)

    #  This command saves the changes made above.
    dbm.db.commit()

    #  This is the format to send SQL commands.
    dbm.query.execute('SELECT * FROM globalObject ORDER BY dateAdded')

    #  This is here for clarity when the db is printed.
    columnNames = ["Unique ID =", "Date added = ", "Name =", "Object Type =",
                   "Creator =", "Date Created =", "Date Modified =", "Date Used =", "Up Votes =", "Down Votes ="]
    k = 0
    
    #  Prints the db.
    for i in dbm.query:
        print "\n"
        for j in i:
            print columnNames[k],
            print j
            if k < 9:
                k += 1
            else:
                k = 0

    #  Be sure to .commit before closing or else the changes won't be saved.
    dbm.query.close()

if __name__ == "__main__":
    main()