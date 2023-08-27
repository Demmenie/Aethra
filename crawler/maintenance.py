#29/10/2022
#Chico Demmenie
#Aethra/Scraper/Maintenance.py

import pymongo
import json
import copy
from MongoAccess import mongoServe
import videohash
import shutil
import datetime

#Creating a class so that each function is contained and easily callable.
class maintenance:

    """A number of functions used to maintain the database."""

    def __init__(self):

        """Initialises the class and gets mongoDB client"""

        keyFile = open("../data/keys.json", "r")
        keys = json.loads(keyFile.read())
        keyFile.close()

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
        self.video2 = self.db.video3
        self.video = self.db.video
        self.allDocs = list(self.video.find({}).sort("index"))
        self.count = len(self.allDocs)

        #self.ms = mongoServe()


    def orderCheck(self):

        """Checks if saved docs are in the correct order."""

        print("orderCheck")

        ordered = True
        lastDoc = None
        for index, doc in enumerate(self.allDocs[:-1]):
            
            nextDoc = self.allDocs[index+1]

            if (int(doc["hashDec"]) > int(nextDoc["hashDec"])):

                print(f"{doc['hashDec']} > {nextDoc['hashDec']}\n")
                ordered = False
                break

        print(f"Ordered: {ordered}")
        return ordered


    def duplicateCheck(self):

        """Checks the database for duplicate videos"""

        ###################################=====================================
        #Needs finishing

        vidDuplicates = []
        for index, eachDoc in enumerate(self.allDocs[:self.count]):

            for otherDoc in self.allDocs[index+1:]:

                if eachDoc["hashHex"] == otherDoc["hashHex"]:

                    vidDuplicates.append((eachDoc["index"], otherDoc["index"]))
        
        postDuplicates = []
        for index, eachDoc in enumerate(self.allDocs[:self.count]):

            for post in eachDoc["postList"]:

                for otherDoc in self.allDocs[index+1:]:

                    for otherPost in otherDoc["postList"]:

                        if (post["id"] == otherPost["id"] and 
                            post["author"] == otherPost["author"]):
                            
                            postDuplicates.append((
                                f"{eachDoc['index']}: {post['id'], post['author']} & "+
                                f"{otherDoc['index']}: {otherPost['id'], otherPost['author']}"))


        return vidDuplicates, postDuplicates


    def reOrder(self):

        """Reorders the database when it's out of order using bubble sort"""

        print("reOrder")

        n = copy.copy(self.count)
        # optimize code, so if the array is already sorted, it doesn't need
        # to go through the entire process

        swapped = False
        # Traverse through all array elements
        for i in range(n):

            print(i)

            # range(n) also work but outer loop will
            # repeat one time more than needed.
            # Last i elements are already in place
            for j in range(0, n-i-1):

                # traverse the array from 0 to n-i-1
                # Swap if the element found is greater
                # than the next element
                a = self.video.find_one({"index": j})["hashDec"]
                b = self.video.find_one({"index": (j + 1)})["hashDec"]
                if (int(a) > int(b)):

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
                    self.vh((f"https://t.me/{post['author']}/{post['id']}"))

                except videohash.exceptions.DownloadFailed as err:
                    print(f"Exception occurred:\n {err}"+
                        "ignoring this post and continuing.")
                    continue
                
                except videohash.exceptions.FFmpegFailedToExtractFrames as err:
                    print(f"[{datetime.datetime.now()}] Caught: {err},",
                        "continuing.")
                    continue


                class postCl:
                    hashHex = self.videoHashHex
                    hashDec = self.videoHashDec
                    platform = "telegram"
                    id = str(post["id"])
                    author = post["author"]
                    text = post["text"]
                    timestamp = post["timestamp"]
                    uTime = post["uploadTime"]

                check = mongoServe().entryCheck(postCl.id, 
                    postCl.author,
                    postCl.hashHex,
                    postCl.hashDec)
                
                if check != None and check != "preexist":
                    print(f"check: {check}")
                    postCl.index = check["index"]
                    mongoServe().addToEntry(postCl)

                elif check == None:
                    mongoServe().newEntry(postCl)


    def reindex(self):

        """Gives each doc a new index."""

        print("reindex")

        videos = self.video.find({})

        for index, eachVid in enumerate(videos):

            self.video.update_one({"index": eachVid["index"]},
                                  {"$set": {"index": index}})


    def vh(self, url):

        """Hashes videos from a url"""

        #Creating the hash and storing the Hex and Decimal
        vHash = videohash.VideoHash(url=url, frame_interval=12)
        self.videoHashHex = vHash.hash_hex
        self.videoHashDec = int(self.videoHashHex, 16)

        #print(self.videoHashHex, self.videoHashDec)

        videoPath = vHash.storage_path
        cutPath = videoPath[:videoPath.find("temp_storage_dir")]

        try:
            shutil.rmtree(cutPath)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

        return self.videoHashHex, self.videoHashDec


if __name__ == "__main__":
    print(maintenance().duplicateCheck())
    
    if not maintenance().orderCheck():
        if input("reOrder? ") in ["y", "Y", "Ye", "ye", "yes", "Yes"]:
            #maintenance().reindex()
            maintenance().reOrder()
            print(maintenance().orderCheck())

    #maintenance().refactor()
    #maintenance().vh("https://twitter.com/aldin_aba/status/1570102341189177346")
