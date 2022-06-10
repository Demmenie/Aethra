#26/04/2022
#Chico Demmenie
#Aethra/MongoAccess.py

#Importing dependencies
import pymongo
from pymongo import MongoClient
import sys
import json
import time

#Creating a class so that each function is contained and easily callable.
class mongoServe:

    """Connects withe the Mongo database."""

    def __init__(self):

        """Initialises the class and gets mongoDB client"""

        keys = json.loads(open("../data/keys.json", "r"))
        conn = ''.join(f"mongodb+srv://Aethra:{keys["mongoPass"]}"+
            "@cluster0.9f6w3.mongodb.net/Aethra?retryWrites=true&w=majority")

        #Setting a 5-second connection timeout so that we're not pinging the
        #server endlessly
        self.client = pymongo.MongoClient(conn,
            tls=True,
            serverSelectionTimeoutMS=5000)

        #Setting the class wide variables that connect to the database and the
        #MilVec collection.
        self.db = self.client.Aethra
        self.TwitVids = self.db.TwitVids


    #A function that checks if the vehicle already exists.
    #---------------------------------------------------------------------------
    def entryCheck(self, url, hashHex):

        """Checks any entry against the database to see if the entry exists."""

        searchValue = {"url": url}
        results = self.MilVec.find(searchValue)

        result = None
        for entry in results:

            if entry["url"] == url:
                result = "preexist"

        if exists == False:

            searchValue = {"hashHex": hashHex}
            results = self.MilVec.find(searchValue)

            for entry in results:

                if entry["hashHex"] == hashHex:
                    result = entry["_id"]

        return result


    #---------------------------------------------------------------------------
    def newEntry(self, hashDec, hashHex, url):

        """Creates a new video entry."""

        length = self.TweetVids.count_documents()

        DataEntry = {
            "_id": length,
            "hashDec": hashDec,
            "hashHex": hashHex,
            "timestamp": time.time(),
            "url": url,
            "postList": []
        }

        self.TwitVids.insert_one(DataEntry)


    #---------------------------------------------------------------------------
    def addToEntry(self, id, url):

        """Adds and extra post to an existing entry."""

        entry = self.TwitVids.find({"_id": id})

        entry["postList"].append({
            "url": url,
            "timestamp": time.time(),
            "uploadTime":
        })

    #---------------------------------------------------------------------------
    def docCount(self):

        """Counts the amount of documents in the database."""

        count = self.TweetVids.count_documents()

        return count


#-------------------------------------------------------------------------------
if __name__ == "__main__":
    mongoServe()
