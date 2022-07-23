#23/07/2022
#Chico Demmenie
#Aethra/MongoAccess.py

#Importing dependencies
import pymongo
from pymongo import MongoClient
import sys
import json
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
        conn = ''.join(f"mongodb+srv://Aethra:{mongoPass}"+
            "@cluster0.73j0r0l.mongodb.net/Aethra?retryWrites=true&w=majority")

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

        print("entryCheck")

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

        #If the url doesn't turn up then we can look to see if the video itself
        #has been seen before
        if result == None:

            searchValue = {"hashHex": hashHex}
            response = self.video.find(searchValue)

            for entry in response:

                if entry["hashHex"] == hashHex:
                    result = entry["index"]

        #Returning what we've found
        return result


    #---------------------------------------------------------------------------
    def newEntry(self, hashDec, hashHex, url, uTime):

        """Creates a new video entry."""

        print("newEntry")

        #Finding the length of the list so far
        length = self.video.count_documents({})

        if length > 1:

            halfLength = length / 2
            modifyLength = copy.copy(halfLength)
            searching = True
            while searching:

                modifyLength = modifyLength / 2
                halfFloor = math.floor(halfLength)
                halfCeil = math.ceil(halfLength)

                floorDoc = self.video.find_one({"index": halfFloor})
                ceilDoc = self.video.find_one({"index": halfCeil})

                if (floorDoc["hashDec"] < hashDec and
                    ceilDoc["hashDec"] > hashDec):

                    index = ceilDoc["index"]
                    searching = False

                elif ceilDoc["hashDec"] < hashDec:
                    halfLength = halfLength + modifyLength

                elif floorDoc["hashDec"] > hashDec:
                    halfLength = halfLength - modifyLength


            for i in range(length, (index-1), -1):
                self.video.update_one({"index": i},
                    {"$set": {"index": i + 1}})

        else:
            doc = self.video.find_one({})

            try:
                if doc["hashDec"] < hashDec:
                    index = 1
                else:
                    index = 0

            except:
                index = 0

        #The id is just the index of this entry.
        dataEntry = {
            "index": index,
            "hashDec": hashDec,
            "hashHex": hashHex,
            "timestamp": time.time(),
            "uploadTime": uTime,
            "url": url,
            "postList": []
        }

        print(dataEntry)

        self.video.insert_one(dataEntry)


    #---------------------------------------------------------------------------
    def addToEntry(self, index, url, uTime):

        """Adds and extra post to an existing entry."""

        print("addToEntry")

        entry = self.video.find({"index": index})

        entry["postList"].append({
            "url": url,
            "timestamp": time.time(),
            "uploadTime": uTime
        })


#-------------------------------------------------------------------------------
if __name__ == "__main__":
    mongoServe()
