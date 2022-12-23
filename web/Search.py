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

        #Opening a connection with the MongoDB Atlas Database
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
        self.video = self.db.video


    #---------------------------------------------------------------------------
    def cleaning(self, query):

        """Cleans up and checks that the query is correct."""

        clean = True
        #First looking to see if it's a website.
        if (query.find("https://", 0, 8) != 0 and
            query.find("http://", 0, 8) != 0):

            clean = False

        #Then looking for character that don't belong in a URL.
        elif query.find(".", 8) < 0 or query.find(".", 8) < 0:  

            clean = False

        else:
            for char in list(query):

                if char not in list("""ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno
                    pqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;="""):

                    clean = False
                    break

        #Returning True or False for if the URL is clean or not.
        return clean


    #---------------------------------------------------------------------------
    def standard(self, url, allDocs):

        """Searches the database in the standard way using binary search."""

        start = time.time()
        #Hashing the video
        try:
            self.videoHash(url)

        #Printing the error if one occurs 
        except videohash.exceptions.DownloadFailed as err:
            print(f"videoHash errored out with exception:\n{err}")
            return "download_failed"

        print(f"Hashing in {time.time() - start}")
        start = time.time()

        #Finding the length of the list so far
        length = len(allDocs)

        #Setting up variables for the binary search.
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

            #If one of the selected documents is the correct one, then we don't
            #Need top continue.
            if floorDoc["hashHex"] == self.hashHex:
                result = copy.copy(floorDoc)
                searching = False

            elif ceilDoc["hashHex"] == self.hashHex:
                result = copy.copy(ceilDoc)
                searching = False

            #If the result doesn't exist, we just return the closest document.
            elif (int(floorDoc["hashDec"]) < self.hashDec and
                int(ceilDoc["hashDec"]) > self.hashDec):

                result = copy.copy(floorDoc)
                searching = False

            #If we haven't found it yet, we keep dividing the list.
            elif int(ceilDoc["hashDec"]) < self.hashDec:
                halfLength = halfLength + modifyLength

            elif int(floorDoc["hashDec"]) > self.hashDec:
                halfLength = halfLength - modifyLength

        print(f"Search in {time.time() - start}")
        start = time.time()

        #Assuming a result is found; a list of 10 videos which are similar is
        #shown to the user.
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

        #Creating hash, setting variables
        vHash = videohash.VideoHash(url=url)
        self.hashHex = vHash.hash_hex
        self.hashDec = int(self.hashHex, 16)

        #After the hash has been found, the temp storage is cleared.
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
