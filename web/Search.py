#30/08/2022
#Chico Demmenie
#Aethra/web/search.py

#Importing dependencies
import pymongo
from pymongo import MongoClient
import videohash
import shutil
import json
import copy
import math
import time

class DBSearch:

    """This class contains functions that search the database for the website"""

    def __init__(self):

        """Class initialisation and database connection."""

        keys = json.loads(open("data/keys.json",
            "r").read())

        mongoPass = keys["mongoPass"]
        mongoCluster = keys["mongoCluster"]
        mongoAccount = keys["mongoAccount"]
        conn = ''.join(f"mongodb+srv://{mongoAccount}:{mongoPass}"+
            f"{mongoCluster}.mongodb.net/{mongoAccount}?retryWrites=true&w=majority")

        #Setting a 5-second connection timeout so that we're not pinging the
        #server endlessly
        self.client = pymongo.MongoClient(conn,
            tls=True,
            serverSelectionTimeoutMS=5000)

        #Setting the class wide variables that connect to the database and the
        #MilVec collection.
        self.db = self.client.Aethra
        self.video = self.db.video


    #---------------------------------------------------------------------------
    def cleaning(self, query):

        """Cleans up and checks that the query is correct."""

        clean = True
        if (query.find("https://", 0, 8) != 0 and
            query.find("http://", 0, 8) != 0):

            clean = False
            print("http")

        elif query.find(".", 8) < 0 or query.find(".", 8) < 0:

            clean = False
            print("./")

        else:
            for char in list(query):

                if char in ["{", "}", "|", "\\", "^", "~", "[", "]", "`"]:

                    print("char")
                    clean = False
                    break

        return clean


    #---------------------------------------------------------------------------
    def standard(self, url):

        """Searches the database in the standard way using binary search."""

        #Hashing the video
        try:
            self.videoHash(url)

        except videohash.exceptions.DownloadFailed:
            return "Download failed"

        responding = False
        while not responding:
            try:
                #Finding the length of the list so far
                length = self.video.count_documents({})

                result = None
                halfLength = length / 2
                modifyLength = copy.copy(halfLength)
                searching = True
                while searching:

                    modifyLength = modifyLength / 2
                    halfFloor = math.floor(halfLength)
                    halfCeil = math.ceil(halfLength)

                    floorDoc = self.video.find_one({"index": halfFloor},
                        projection={'_id': False})
                    ceilDoc = self.video.find_one({"index": halfCeil},
                        projection={'_id': False})

                    if floorDoc["hashHex"] == self.hashHex:
                        result = copy.copy(floorDoc)
                        searching = False

                    elif ceilDoc["hashHex"] == self.hashHex:
                        result = copy.copy(ceilDoc)
                        searching = False

                    elif (int(floorDoc["hashDec"]) < self.hashDec and
                        int(ceilDoc["hashDec"]) > self.hashDec):

                        index = ceilDoc["index"]
                        searching = False

                    elif int(ceilDoc["hashDec"]) < self.hashDec:
                        halfLength = halfLength + modifyLength

                    elif int(floorDoc["hashDec"]) > self.hashDec:
                        halfLength = halfLength - modifyLength

                if result != None:
                    returnList = []
                    returnList.append(result)
                    returnList.append(self.video.find_one({"index": (result["index"] + 1)},
                        projection={'_id': False}))
                    returnList.append(self.video.find_one({"index": (result["index"] - 1)},
                        projection={'_id': False}))

                    return returnList

                else:
                    return result

                responding = True

            except pymongo.errors.NetworkTimeout:
                time.sleep(60)

            except pymongo.errors.ServerSelectionTimeoutError:
                time.sleep(60)


    #---------------------------------------------------------------------------
    def videoHash(self, url):

        """Hashes videos for storage."""

        vHash = videohash.VideoHash(url=url)
        self.hashHex = vHash.hash_hex
        self.hashDec = int(self.hashHex, 16)

        videoPath = vHash.storage_path
        cutPath = videoPath[:videoPath.find("temp_storage_dir")]

        shutil.rmtree(cutPath)


if __name__ == "__main__":

    print(DBSearch().standard(""))
