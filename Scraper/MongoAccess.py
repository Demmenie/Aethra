#02/09/2022
#Chico Demmenie
#Aethra/Scraper/MongoAccess.py

#Importing dependencies
import pymongo
from pymongo import MongoClient
import sys
import json
import time
import datetime
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
    def entryCheck(self, url, hashHex, hashDec):

        """Checks any entry against the database to see if the entry exists."""

        print(f"[{datetime.datetime.now()}] entryCheck()")

        #requesting all the documents in the database.
        self.allDocs = list(self.video.find({}).sort("index"))
        length = len(self.allDocs)

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

            elif int(ceilDoc["hashDec"]) < hashDec:
                halfLength = halfLength + modifyLength

            elif int(floorDoc["hashDec"]) > hashDec:
                halfLength = halfLength - modifyLength


            #If either of the docs are None then we've reached the top
            #or bottom.
            elif modifyLength == 0 and int(ceilDoc["hashDec"]) > hashDec:

                reult = None
                searching = False

            elif modifyLength == 0 and int(floorDoc["hashDec"]) < hashDec:

                reult = None
                searching = False


            if result != None:
                for post in result["postList"]:

                    if post["url"] == url:
                        result = "preexist"
                        break


        #Returning what we've found
        print(f"[{datetime.datetime.now()}] {result}")
        return result


    #---------------------------------------------------------------------------
    def newEntry(self, hashDec, hashHex, url, uTime):

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
                    if floorDoc != None and ceilDoc != None:

                        if (int(floorDoc["hashDec"]) < hashDec and
                            int(ceilDoc["hashDec"]) > hashDec):

                            index = ceilDoc["index"]
                            searching = False

                        elif int(ceilDoc["hashDec"]) < hashDec:
                            halfLength = halfLength + modifyLength

                        elif int(floorDoc["hashDec"]) > hashDec:
                            halfLength = halfLength - modifyLength

                    #If either of the docs are None then we've reached the top
                    #or bottom.
                    elif floorDoc == None and int(ceilDoc["hashDec"]) > hashDec:

                        index = ceilDoc["index"]
                        searching = False

                    elif ceilDoc == None and int(floorDoc["hashDec"]) < hashDec:

                        index = floorDoc["index"] + 1
                        searching = False


                #Once we've found our index, we need to change the index of
                #every document that's higher.
                for i in range(length, (index-1), -1):
                    self.video.update_one({"index": i},
                        {"$set": {"index": i + 1}})


                #Setting up the details in the entry.
                dataEntry = {
                    "index": index,
                    "hashDec": str(hashDec),
                    "hashHex": hashHex,
                    "postList": [{"url": url,
                    "timestamp": time.time(),
                    "uploadTime": uTime
                    }]
                }

                self.video.insert_one(dataEntry)
                print(f"[{datetime.datetime.now()}]", dataEntry)

                responding = True

            except pymongo.errors.NetworkTimeout as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}, sleeping 60")
                time.sleep(60)

            except pymongo.errors.ServerSelectionTimeoutError as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}, sleeping 60")
                time.sleep(60)




    #---------------------------------------------------------------------------
    def addToEntry(self, index, url, uTime):

        """Adds and extra post to an existing entry."""

        print(f"[{datetime.datetime.now()}] addToEntry()")

        responding = False
        while not responding:
            try:
                #First we find the entry that needs updating.
                entry = self.video.find_one({"index": index})

                #Then we update the entry to include the new post.
                if entry != None:
                    self.video.update_one({"index": index},
                        {"$push": {"postList":
                        {"url": url,
                        "timestamp": time.time(),
                        "uploadTime": uTime}}})

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
