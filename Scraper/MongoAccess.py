#08/04/2022
#Chico Demmenie
#Aethra/MongoAccess.py

#Importing dependencies
import pymongo
from pymongo import MongoClient
import sys
import json

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

        #Setting the class wide variables that connect to the databse and the
        #MilVec collection.
        self.db = self.client.Aethra
        self.TwitVids = self.db.TwitVids


    #A function that checks if the vehicle already exists.
    #---------------------------------------------------------------------------
    def entryCheck(self, url, hashHex):

        """Checks any entry against the database to see if the entry exists."""

        searchValue = {"url": url}

        results = self.MilVec.find(searchValue)

        exists = False
        for entry in results:

            if entry["url"] == url:
                exists = True
                break

        if exists =


    #---------------------------------------------------------------------------
    def newEntry(self, ):

        """Creates a new video entry."""

        DataEntry = {

        }


#-------------------------------------------------------------------------------
if __name__ == "__main__":
    mongoServe()
