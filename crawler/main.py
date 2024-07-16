#16/07/2024
#Chico Demmenie
#Aethra/crawler/main.py

from snscrape.modules import *
import datetime
import videohash2
from MongoAccess import mongoServe
from dbAccess import dbAccess
from utils import utils


class main:

    """The main class for the crawler"""

    def __init__(self):

        """
        Desc: Initialises the core class functions.
        """

        #Initialising dbAccess
        self.dba = dbAccess()
        self.utils = utils()


    #---------------------------------------------------------------------------
    def main(self):

        """
        Desc: Takes posts from queue, hashes them and adds them to the DB.
        """

        while True:

            post = self.dba.popQPost()
            print(post)
            
            if post:
                postOb = utils.postOb()
                postOb.platform = post[1]
                postOb.id = post[2]
                postOb.author = post[3]
                postOb.text = post[4]
                postOb.timestamp = post[5]
                postOb.uTime = post[6]
                postOb.vidLength = post[7]

                url = f"https://t.me/{postOb.author}/{postOb.id}?single"

                try:
                    postOb.hashHex, postOb.hashDec = self.utils.videoHash(url)

                except videohash2.exceptions.DownloadFailed as err:
                    print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "continuing.")
                    continue

                except videohash2.exceptions.FFmpegFailedToExtractFrames as err:
                    print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "continuing.")
                    continue

                
                #Searching the database to see if this video already
                #exists.
                result = self.dba.vidCheck(postOb.platform,
                                           postOb.id,
                                           postOb.author,
                                           postOb.id,
                                           postOb.hashHex)

                #Adding the new tweet to an existing entry
                if result != None and result != "preexist":

                    postOb.index = result[0]
                    self.dba.addPost(postOb, result[1])

                #Creating a new entry for a new tweet.
                elif result == None:

                    self.dba.newVid(postOb)


if __name__ == "__main__":

    main().main()
