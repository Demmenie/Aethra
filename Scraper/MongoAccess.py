#29/08/2022
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


    #A function that checks if the vehicle already exists.
    #---------------------------------------------------------------------------
    def entryCheck(self, url, hashHex):

        """Checks any entry against the database to see if the entry exists."""

        print(f"[{datetime.datetime.now()}] entryCheck()")

        responding = False
        while not responding:
            try:
                #Searching to see if the url turns up in the database
                searchValue = {"url": url}
                response = self.video.find(searchValue)

                #Looking through to confirm if that url is in the response
                result = None
                for entry in response:

                    if entry["url"] == url:
                        result = "preexist"

                    else:
                        for post in entry["postList"]:

                            if post["url"] == url:
                                result = "preexist"

                #If the url doesn't turn up then we can look to see if the video
                #itself has been seen before
                if result == None:

                    searchValue = {"hashHex": hashHex}
                    response = self.video.find(searchValue)

                    for entry in response:

                        if entry["hashHex"] == hashHex and entry["url"] != url:
                            result = entry["index"]

                        else:
                            for post in entry["postList"]:

                                if post["url"] == url:
                                    result = "preexist"

                responding = True

            except pymongo.errors.NetworkTimeout as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}, sleeping 60")
                time.sleep(60)

            except pymongo.errors.ServerSelectionTimeoutError as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}, sleeping 60")
                time.sleep(60)

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
                #Finding the length of the list so far
                length = self.video.count_documents({})

                #Creating a while loop to do binary search on the database.
                halfLength = length / 2
                modifyLength = copy.copy(halfLength)
                searching = True
                while searching:

                    modifyLength = modifyLength / 2
                    halfFloor = math.floor(halfLength)
                    halfCeil = math.ceil(halfLength)

                    floorDoc = self.video.find_one({"index": halfFloor})
                    ceilDoc = self.video.find_one({"index": halfCeil})

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
                    "timestamp": time.time(),
                    "uploadTime": uTime,
                    "url": url,
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


#-------------------------------------------------------------------------------
if __name__ == "__main__":
    mongoServe()
