#14/09/2022
#Chico Demmenie
#Aethra/Scraper/MongoAccess.py

#Importing dependencies
import pymongo
from pymongo import MongoClient
import sys
import json
import time
import datetime
import time
import copy
import math

#Creating a class so that each function is contained and easily callable.
class mongoServe:

    """Connects with the the Mongo database."""

    def __init__(self):

        """Initialises the class and gets mongoDB client"""

        keys = json.loads(open("../data/keys.json", "r").read())

        mongoPass = keys["mongoPass"]
        mongoCluster = keys["mongoCluster"]
        mongoAccount = keys["mongoAccount"]
        conn = ''.join(f"mongodb+srv://{mongoAccount}:{mongoPass}"+
            f"{mongoCluster}.mongodb.net/{mongoAccount}"+
            "?retryWrites=true&w=majority")

        #Setting a 5-second connection timeout so that we're not pinging the
        #server endlessly
        self.client = pymongo.MongoClient(conn,
            tls=True,
            serverSelectionTimeoutMS=5000)

        #Setting the class wide variables that connect to the database and the
        #MilVec collection.
        self.db = self.client.Aethra
        self.video = self.db.video
        self.backup = self.db.backup


    #A function that checks if the vehicle already exists.
    #---------------------------------------------------------------------------
    def entryCheck(self, id, hashHex, hashDec):

        """Checks any entry against the database to see if the entry exists."""

        print(f"[{datetime.datetime.now()}] entryCheck()")

        responding = False
        while not responding:

            try:
                #requesting all the documents in the database.
                self.allDocs = list(self.video.find({}).sort("index"))
                length = len(self.allDocs)
                responding = True

            except pymongo.errors.ServerSelectionTimeoutError as err:

                print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                    "sleeping 60 secs."))
                time.sleep(60)


        #Defining values for the while loop
        result = None
        halfLength = length / 2
        modifyLength = copy.copy(halfLength)
        searching = True
        while searching:

            modifyLength = modifyLength / 2
            halfFloor = math.floor(halfLength)
            halfCeil = math.ceil(halfLength)

            floorDoc = self.allDocs[halfFloor]
            ceilDoc = self.allDocs[halfCeil]


            if floorDoc["hashHex"] == hashHex:
                result = floorDoc
                searching = False

            elif ceilDoc["hashHex"] == hashHex:
                result = ceilDoc
                searching = False

            elif (int(floorDoc["hashDec"]) < hashDec and
                int(ceilDoc["hashDec"]) > hashDec):

                result = None
                searching = False
                break

            #If either of the docs are None then we've reached the top
            #or bottom.
            elif floorDoc["index"] == 0 and int(floorDoc["hashDec"]) > hashDec:

                result = None
                searching = False

            elif ceilDoc["index"] == (length - 1) and (int(ceilDoc["hashDec"]) <
                hashDec):

                result = None
                searching = False


            #Modifying the halfLength for next loop.
            elif int(ceilDoc["hashDec"]) < hashDec:
                halfLength = halfLength + modifyLength

            elif int(floorDoc["hashDec"]) > hashDec:
                halfLength = halfLength - modifyLength


            if result != None:
                for post in result["postList"]:

                    if post["id"] == str(id):
                        result = "preexist"
                        break


        #Returning what we've found
        print(f"[{datetime.datetime.now()}] {result}")
        return result


    #---------------------------------------------------------------------------
    def newEntry(self, post):

        """Creates a new video entry."""

        print(f"[{datetime.datetime.now()}] newEntry()")

        responding = False
        while not responding:
            try:
                #requesting all the documents in the database.
                self.allDocs = list(self.video.find({}).sort("index"))
                length = len(self.allDocs)

                #Creating a while loop to do binary search on the database.
                halfLength = length / 2
                modifyLength = copy.copy(halfLength)
                searching = True
                while searching:

                    modifyLength = modifyLength / 2
                    halfFloor = math.floor(halfLength)
                    halfCeil = math.ceil(halfLength)

                    floorDoc = self.allDocs[halfFloor]
                    ceilDoc = self.allDocs[halfCeil]

                    #We check the document above and below to figure out if we
                    #need to go higher or lower.
                    if (int(floorDoc["hashDec"]) < post.hashDec and
                        int(ceilDoc["hashDec"]) > post.hashDec):

                        index = ceilDoc["index"]
                        searching = False

                    #If either of the docs are None then we've reached the top
                    #or bottom.
                    elif floorDoc["index"] == 0 and (int(floorDoc["hashDec"]) >
                        post.hashDec):

                        index = floorDoc["index"]
                        searching = False

                    elif (ceilDoc["index"] == (length - 1) and
                        int(ceilDoc["hashDec"]) < post.hashDec):

                        index = ceilDoc["index"]
                        searching = False


                    elif int(ceilDoc["hashDec"]) < post.hashDec:
                        halfLength = halfLength + modifyLength

                    elif int(floorDoc["hashDec"]) > post.hashDec:
                        halfLength = halfLength - modifyLength


                #Once we've found our index, we need to change the index of
                #every document that's higher.
                for i in range(length, (index-1), -1):
                    self.video.update_one({"index": i},
                        {"$set": {"index": i + 1}})


                #Setting up the details in the entry.
                dataEntry = {
                    "index": index,
                    "hashDec": str(post.hashDec),
                    "hashHex": post.hashHex,
                    "postList": [{"platform": post.platform,
                    "id": post.id,
                    "author": post.author,
                    "text": post.text,
                    "timestamp": time.time(),
                    "uploadTime": post.uTime
                    }]
                }

                self.video.insert_one(dataEntry)
                print(f"[{datetime.datetime.now()}]", str(dataEntry))

                responding = True

            except pymongo.errors.NetworkTimeout as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}, sleeping 60")
                time.sleep(60)

            except pymongo.errors.ServerSelectionTimeoutError as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}, sleeping 60")
                time.sleep(60)


    #---------------------------------------------------------------------------
    def addToEntry(self, post):

        """Adds and extra post to an existing entry."""

        print(f"[{datetime.datetime.now()}] addToEntry()")

        responding = False
        while not responding:
            try:
                #First we find the entry that needs updating.
                entry = self.video.find_one({"index": post.index})

                #Then we update the entry to include the new post.
                if entry != None:
                    self.video.update_one({"index": post.index},
                        {"$push": {"postList":
                        {"platform": post.platform,
                        "id": post.id,
                        "author": post.author,
                        "text": post.text,
                        "timestamp": time.time(),
                        "uploadTime": post.uTime}}})

                    print(f"[{datetime.datetime.now()}], Updated: {entry}")

                responding = True

            except pymongo.errors.NetworkTimeout as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}, sleeping 60")
                time.sleep(60)

            except pymongo.errors.ServerSelectionTimeoutError as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}, sleeping 60")
                time.sleep(60)


    #---------------------------------------------------------------------------
    def fullBackup(self):

        """Backs up the database."""

        print(f"[{datetime.datetime.now()}] Backing up database.")

        self.allDocs = list(self.video.find({}).sort("index"))

        for doc in self.allDocs:

            self.backup.update_one({"index": doc["index"]},
                {"$set": {"index": doc["index"],
                "hashHex": doc["hashHex"],
                "hashDec": doc["hashDec"],
                "postList": doc["postList"]}}, upsert=True)


#-------------------------------------------------------------------------------
if __name__ == "__main__":
    mongoServe()
