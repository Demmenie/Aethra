#16/07/2024
#Chico Demmenie
#Aethra/crawler/telegram.py

import snscrape
from snscrape.modules import telegram as tg
import videohash2
import time
import datetime
from dbAccess import dbAccess
from utils import utils


class telegram:

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
        Desc: Saves videos from telegram channels.
        """

        self.maxUsers = self.dba.getMaxTelUsers()

        #Going through the channel list to find new posts to add to the database.
        for userIndex in range(0, self.maxUsers):

            channel = self.dba.getTelUser(userIndex)[1]

            print("Checking:", channel)

            try:
                print(f"[{datetime.datetime.now()}] Getting current posts from",
                        channel)
                posts = tg.TelegramChannelScraper(channel).get_items()

            except snscrape.base.ScraperException as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "continuing.")
                continue

            try:
                for index, post in enumerate(posts):
                    
                    if index > 15:
                        break

                    #First checking for mentioned accounts that we might not have
                    #stored yet.
                    self.findTelUsers(post.outlinks)

                    lastSlash = post.url.rfind('/')
                    postID = post.url[lastSlash+1:]
                    url = f"https://t.me/{channel}/{postID}?single"

                    #Checking to see if the post contains a video.
                    try:
                        vidLength = videohash2.video_duration(url=url)

                    except videohash2.exceptions.DownloadFailed as err:
                        print(f"[{datetime.datetime.now()}] Caught: {err}",
                            "continuing.")
                        continue

                    except videohash2.exceptions.FFmpegFailedToExtractFrames as err:
                        print(f"[{datetime.datetime.now()}] Caught: {err}",
                            "continuing.")
                        continue

                    if vidLength > 300:
                        continue
                    
                    postInQ = self.dba.findQPost("telegram", channel, postID)
                    print("Post in Queue:", postInQ)

                    if not postInQ:
                        postExists = self.dba.postCheck("telegram",
                                                        channel, postID)

                        if not postExists:

                            postOb = self.utils.postOb()
                            postOb.platform = "telegram"
                            postOb.author = channel
                            postOb.id = postID
                            postOb.text = post.content
                            postOb.timestamp = time.time()
                            postOb.uTime = datetime.datetime.timestamp(post.date)
                            postOb.vidLength = vidLength

                            print(post)

                            self.dba.addQPost(postOb)


            except snscrape.base.ScraperException as err:
                print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                    "waiting 60 secs and continuing."))
                time.sleep(60)
                continue


    #---------------------------------------------------------------------------
    def findTelUsers(self, outlinks):

        """
        Desc: Finds new users in the outlinks of telegram posts.
        """

        print(f"[{datetime.datetime.now()}] findTelUsers()")

        for link in outlinks:

            if link.find("https://t.me/s/+") != -1:
                continue

            elif link.find("https://t.me/+") != -1:
                continue
        
            elif link.find("https://t.me/s/") != -1:
                telURL = "https://t.me/s/"
                
            elif link.find("https://t.me/") != -1:
                telURL = "https://t.me/"
            
            else:
                continue


            nameStart = link.rfind(telURL) + len(telURL)

            if link[len(telURL):].find("/") == -1 and link.find("?") == -1:
                username = link[nameStart:]

            elif link.find("?") == -1:
                nameEnd = link.rfind("/")
                username = link[nameStart:nameEnd]

            else:
                continue
            

            userExists = self.dba.findTelUser(username)
            if not userExists:
                print(f"[{datetime.datetime.now()}] {username} added to telegram list.")
                self.dba.addTelUser(username)


if __name__ == "__main__":

    while True:
        telegram().main()