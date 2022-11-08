#08/11/2022
#Chico Demmenie
#Aethra/web/search.py

#Importing dependencies
import pymongo
from pymongo import MongoClient
from operator import itemgetter
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
            f"{mongoCluster}.mongodb.net/{mongoAccount}?retryWrites=true&w="+
            "majority")

        #Setting a 5-second connection timeout so that we're not pinging the
        #server endlessly
        self.client = pymongo.MongoClient(conn,
            tls=True,
            serverSelectionTimeoutMS=5000)

        #Setting the class wide variables that connect to the database and the
        #video collection.
        self.db = self.client.Aethra
        self.video = self.db.video2


    #---------------------------------------------------------------------------
    def cleaning(self, query):

        """Cleans up and checks that the query is correct."""

        clean = True
        if (query.find("https://", 0, 8) != 0 and
            query.find("http://", 0, 8) != 0):

            clean = False

        elif query.find(".", 8) < 0 or query.find(".", 8) < 0:  

            clean = False

        else:
            for char in list(query):

                if char not in list("""ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno
                    pqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;="""):

                    clean = False
                    break

        return clean


    #---------------------------------------------------------------------------
    def standard(self, url, allDocs):

        """Searches the database in the standard way using binary search."""

        start = time.time()
        #Hashing the video
        try:
            self.videoHash(url)

        except videohash.exceptions.DownloadFailed as err:
            print(f"videoHash errored out with exception:\n{err}")
            return "download_failed"

        print(f"Hashing in {time.time() - start}")
        start = time.time()
        #Finding the length of the list so far
        length = len(allDocs)

        result = None
        halfLength = length / 2
        modifyLength = copy.copy(halfLength)
        searching = True
        while searching:

            modifyLength = modifyLength / 2
            halfFloor = math.floor(halfLength)
            halfCeil = math.ceil(halfLength)

            floorDoc = allDocs[halfFloor]
            ceilDoc = allDocs[halfCeil]

            if floorDoc["hashHex"] == self.hashHex:
                result = copy.copy(floorDoc)
                searching = False

            elif ceilDoc["hashHex"] == self.hashHex:
                result = copy.copy(ceilDoc)
                searching = False

            elif (int(floorDoc["hashDec"]) < self.hashDec and
                int(ceilDoc["hashDec"]) > self.hashDec):

                result = copy.copy(floorDoc)
                searching = False

            elif int(ceilDoc["hashDec"]) < self.hashDec:
                halfLength = halfLength + modifyLength

            elif int(floorDoc["hashDec"]) > self.hashDec:
                halfLength = halfLength - modifyLength

        print(f"Search in {time.time() - start}")
        start = time.time()
        if result != None:
            returnList = []
            returnList.append(result)

            for i in range(5):
                returnList.append(allDocs[result["index"] + i])
                returnList.append(allDocs[result["index"] - i])

            for index, video in enumerate(returnList):
                video["sDiff"] = abs(int(video["hashDec"]) - self.hashDec)

            returnList = sorted(returnList, key=itemgetter('sDiff')) 
            print(f"Sorting in {time.time() - start}")

            return json.dumps(returnList)

        else:
            return result


    #---------------------------------------------------------------------------
    def videoHash(self, url):

        """Hashes videos for storage."""

        vHash = videohash.VideoHash(url=url, frame_interval=12)
        self.hashHex = vHash.hash_hex
        self.hashDec = int(self.hashHex, 16)

        videoPath = vHash.storage_path
        cutPath = videoPath[:videoPath.find("temp_storage_dir")]

        shutil.rmtree(cutPath)


    #---------------------------------------------------------------------------
    def updateList(self):

        """Updates the list of videos."""

        response = list(self.video.find({}, 
            projection={'_id': False}).sort("index"))
        return response


if __name__ == "__main__":

    print(DBSearch().cleaning(""))
