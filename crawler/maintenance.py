#29/10/2022
#Chico Demmenie
#Aethra/Scraper/Maintenance.py

import pymongo
import json
import copy
from MongoAccess import mongoServe
import videohash
import shutil

#Creating a class so that each function is contained and easily callable.
class maintenance:

    """A number of functions used to maintain the database."""

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
        self.allDocs = list(self.video.find({}).sort("index"))
        self.count = self.video.count_documents({})

        #self.ms = mongoServe()


    def orderCheck(self):

        """Checks if saved docs are in the correct order."""

        print("orderCheck")

        ordered = True
        lastDoc = None
        for doc in range(0, self.count):

            thisDoc = self.video.find_one({"index": doc})
            if lastDoc != None and thisDoc["hashDec"] < lastDoc["hashDec"]:

                ordered = False
                break

            else:
                lastDoc = copy.copy(thisDoc)

        return ordered


    def duplicateCheck(self):

        """Checks the database for duplicate videos"""

        ###################################=====================================
        #Needs finishing

        duplicates = []
        for index, eachDoc in enumerate(self.allDocs[:self.count]):

            for otherDoc in self.allDocs[index+1:]:

                if eachDoc["hashHex"] == otherDoc["hashHex"]:

                    duplicates.append((eachDoc["index"], otherDoc["index"]))

        return duplicates


    def reOrder(self):

        """Reorders the database when it's out of order using bubble sort"""

        print("reOrder")

        n = copy.copy(self.count)
        # optimize code, so if the array is already sorted, it doesn't need
        # to go through the entire process

        swapped = False
        # Traverse through all array elements
        for i in range(n-1):

            # range(n) also work but outer loop will
            # repeat one time more than needed.
            # Last i elements are already in place
            for j in range(0, n-i-1):

                # traverse the array from 0 to n-i-1
                # Swap if the element found is greater
                # than the next element
                a = self.video.find_one({"index": j})["hashDec"]
                b = self.video.find_one({"index": (j + 1)})["hashDec"]
                if a > b:

                    swapped = True
                    self.video.update_one({"index": j, "hashDec": a},
                        {"$set": {"index": (j + 1)}})
                    self.video.update_one({"index": (j + 1), "hashDec": b},
                        {"$set": {"index": j}})

            if not swapped:
                # if we haven't needed to make a single swap, we
                # can just exit the main loop.
                return swapped

        return self.video.find({})

    
    def refactor(self):

        """Transfers the database from one collection to another, transforming
            it in some way."""

        for doc in self.allDocs:

            for post in doc["postList"]:

                try:
                    self.vh((f"https://twitter.com/{post['author']}/status/"+
                        post["id"]))

                except videohash.exceptions.DownloadFailed as err:
                    print(f"Exception occurred:\n {err}"+
                        "ignoring this post and continuing.")
                    continue

                class postCl:
                    hashHex = self.videoHashHex
                    hashDec = self.videoHashDec
                    platform = "twitter"
                    id = str(post["id"])
                    author = post["author"]
                    text = post["text"]
                    timestamp = post["timestamp"]
                    uTime = post["uploadTime"]

                check = mongoServe().entryCheck(postCl.id, postCl.hashHex,
                    postCl.hashDec)
                
                if check != None and check != "preexist":
                    print(f"check: {check}")
                    postCl.index = check["index"]
                    mongoServe().addToEntry(postCl)

                elif check == None:
                    mongoServe().newEntry(postCl)


    def vh(self, url):

        """Hashes videos from a url"""

        #Creating the hash and storing the Hex and Decimal
        vHash = videohash.VideoHash(url=url, frame_interval=12)
        self.videoHashHex = vHash.hash_hex
        self.videoHashDec = int(self.videoHashHex, 16)

        videoPath = vHash.storage_path
        cutPath = videoPath[:videoPath.find("temp_storage_dir")]

        shutil.rmtree(cutPath)


if __name__ == "__main__":
    #if not maintenance().orderCheck():
        #if input("reOrder? ") in ["y", "Y", "Ye", "ye", "yes", "Yes"]:
            #maintenance().reOrder()
            #print(maintenance().orderCheck())

    print(maintenance().duplicateCheck())
    maintenance().refactor()
