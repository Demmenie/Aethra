#13/07/2024
#Chico Demmenie
#Aethra/Scraper/Maintenance.py

import pymongo
import json
import bson
import copy
from dbAccess import dbAccess
from utils import utils
import videohash2
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
        self.video = self.db.video3
        #self.allDocs = list(self.video.find({}).sort("index"))
        self.count = self.video.count_documents({})
        self.lists = list(self.db.lists.find({"_id": bson.ObjectId("64adabd75fa42c8c80b3931b")}))[0]

        self.dba = dbAccess()
        self.utils = utils()


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

        print(f"[{datetime.datetime.now()}] refactor()")
        

        #Cycling through each video in the mongo DB
        for index in range(0, self.count):

            doc = self.video.find_one({"index": index})

            print("Video Index:", doc["index"])
            
            #Then through each post in the video
            for post in doc["postList"]:

                print(post)

                postCheck = self.dba.postCheck(post["platform"], post["author"],
                    post["id"])
                
                if postCheck != "preexist":

                    #Looking for the video and rehashing it, both to check that it's
                    #still there and to make sure the hash is good.
                    try:
                        url = f"https://t.me/{post['author']}/{post['id']}?single"

                        print(url)

                        vidLength = videohash2.video_duration(url=url)

                        if vidLength < 300:

                            vidHashHex, vidHashDec = self.utils.videoHash(url)

                        else:
                            continue

                    except videohash2.exceptions.DownloadFailed as err:
                        print(f"Exception occurred:\n {err}"+
                            "ignoring this post and continuing.")
                        continue
                    
                    except videohash2.exceptions.FFmpegFailedToExtractFrames as err:
                        print(f"[{datetime.datetime.now()}] Caught: {err},",
                            "continuing.")
                        continue
                    
                    #Creating the post class
                    class postCl:
                        hashHex = vidHashHex
                        hashDec = vidHashDec
                        platform = "telegram"
                        id = str(post["id"])
                        author = post["author"]
                        text = post["text"]
                        timestamp = post["timestamp"]
                        uTime = post["uploadTime"]
                    
                    #Checking to see if the post/video already exist.
                    check = self.dba.vidCheck(postCl.platform, postCl.author,
                        postCl.id, postCl.hashHex)
                    
                    #If the video already exists we add the post to the video.
                    if check != None and check != "preexist":
                        print(f"check: {check}")
                        postCl.index = check[0]
                        self.dba.addPost(postCl, check[1])

                    #If the video doesn't exist yet, we make a new video entry.
                    elif check == None:
                        self.dba.newVid(postCl)

                #Removing the post to save memory
                doc["postList"].remove(post)
                
            #Removeing the video to save memory.
            #self.allDocs.remove(doc)


    def moveList(self):

        print("Getting list from MongoDB.")
        #print(self.lists)
        telList = self.lists["telegram"]

        for index, user in enumerate(telList):

            print(index, user)
            if list(user)[0] != "+":
                
                result = self.dba.findTelUser(user)
                print(result)

                if result == None:
                    self.dba.addTelUser(user)


if __name__ == "__main__":
    #if not maintenance().orderCheck():
        #if input("reOrder? ") in ["y", "Y", "Ye", "ye", "yes", "Yes"]:
            #maintenance().reOrder()
            #print(maintenance().orderCheck())

    #print(maintenance().duplicateCheck())
    #print(maintenance().orderCheck)
    maintenance().refactor()
    #maintenance().vh("https://twitter.com/aldin_aba/status/1570102341189177346")
