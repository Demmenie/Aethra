#11/07/2023
#Chico Demmenie
#Aethra/crawler/history.py

from snscrape.modules import *
import videohash
import time
import datetime
import json
from MongoAccess import mongoServe
from main import main

class history():

    """The main class for the crawler"""

    def __init__(self):

        """
        Desc: Initialises the core class functions.
        """

        #Retrieving OAuth Twitter keys and lists
        keys = open("../data/keys.json", "r")
        self.keys = json.load(keys)
        keys.close()

        lists = open("../data/lists.json", "r")
        self.lists = json.loads(lists.read())
        lists.close()

        self.running = True
        while self.running:

            self.telegram()

    #---------------------------------------------------------------------------
    class postOb:

        """A single class shared across all platforms to add to the database."""

        hashDec = None
        hashHex = None
        platform = None
        id = None
        author = None
        text = None
        timestamp = time.time()
        uTime = None


            
    #---------------------------------------------------------------------------
    def telegram(self):

        """
        Desc: Saves videos from telegram channels.
        """

        #Going through the channel list to find new posts to add to the database.
        for channel in self.lists["telegram"]:

            posts = telegram.TelegramChannelScraper(channel).get_items()

            for post in posts:
                
                #First checking for montioned accounts that we might not have
                #stored yet.
                self.lists = main().findTelUsers(post.outlinks, self.lists)

                #Now looking to see if the post has a video in it.
                try:
                    lastSlash = post.url.rfind('/')
                    postID = post.url[lastSlash+1:]
                    url = f"https://t.me/{channel}/{postID}"

                    hashHex, hashDec = main().videoHash(url)

                    postOb = self.postOb()
                    postOb.hashDec = hashDec
                    postOb.hashHex = hashHex
                    postOb.platform = "telegram"
                    postOb.id = postID
                    postOb.author = channel
                    postOb.text = post.content
                    postOb.uTime = datetime.datetime.timestamp(post.date)
                    
                    main().resolve(postOb, hashHex, hashDec)


                except videohash.exceptions.DownloadFailed as err:
                    print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "continuing.")
                    continue

                except videohash.exceptions.FFmpegFailedToExtractFrames as err:
                    print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "continuing.")
                    continue

if __name__ == "__main__":
    history()