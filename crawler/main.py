#11/07/2023
#Chico Demmenie
#Aethra/crawler/main.py

import tweepy
from snscrape.modules import *
import requests
import urllib3
import http
import time
import datetime
import json
import shutil
import videohash
from MongoAccess import mongoServe


class main:

    """The main class for the crawler"""

    def __init__(self):

        """
        Desc: Initialises the core class functions.
        """

        #Retrieving OAuth Twitter keys and lists
        keys = open("../data/keys.json", "r")
        self.keys = json.load(keys)
        keys.close()

        #Setting up tweepy api (V1.1)
        #auth = tweepy.OAuth1UserHandler(
           #consumer_key=self.keys["apiKey"],
           #consumer_secret=self.keys["apiSecret"],
           #access_token=self.keys["accessToken"],
           #access_token_secret=self.keys["accessSecret"])

        #self.api = tweepy.API(auth)

        #Setting up Tweepy Client (V2.0)
        #self.client = tweepy.Client(
            #bearer_token=self.keys["bearerToken"],
            #consumer_key=self.keys["apiKey"],
            #consumer_secret=self.keys["apiSecret"],
            #access_token=self.keys["accessToken"],
            #access_token_secret=self.keys["accessSecret"],
            #wait_on_rate_limit=True)
        
        self.lists = mongoServe().getLists()

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

            try:
                print(f"[{datetime.datetime.now()}] Getting current posts from",
                       channel)
                posts = telegram.TelegramChannelScraper(channel).get_items()

            except snscrape.base.ScraperException as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "continuing.")
                continue


            for index, post in enumerate(posts):
                
                if index > 9:
                    break


                #First checking for montioned accounts that we might not have
                #stored yet.
                #First checking for montioned accounts that we might not have
                #stored yet.
                self.lists = self.findTelUsers(post.outlinks, self.lists)

                #Now looking to see if the post has a video in it.
                try:
                    lastSlash = post.url.rfind('/')
                    postID = post.url[lastSlash+1:]
                    url = f"https://t.me/{channel}/{postID}"

                    self.videoHash(url)

                    postOb = self.postOb()
                    postOb.hashDec = self.videoHashDec
                    postOb.hashHex = self.videoHashHex
                    postOb.platform = "telegram"
                    postOb.id = postID
                    postOb.author = channel
                    postOb.text = post.content
                    postOb.uTime = datetime.datetime.timestamp(post.date)
                    
                    self.resolve(postOb, self.videoHashHex, self.videoHashDec)


                except videohash.exceptions.DownloadFailed as err:
                    print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "continuing.")
                    continue

                except videohash.exceptions.FFmpegFailedToExtractFrames as err:
                    print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "continuing.")
                    continue


    #---------------------------------------------------------------------------
    def twitter(self):

        """
        Desc: Saves videos from Twitter.
        """

        #Going through the lists to find new tweets to add to the database.
        for list in self.lists["twitter"]:

            print(f"\n[{datetime.datetime.now()}] {list}")

            while True:
                try:
                    #Requesting a list of tweets from twitter.
                    list = self.client.get_list_tweets(list,
                        expansions="attachments.media_keys",
                        max_results=10)
                    break

                except tweepy.errors.TweepyException:
                    time.sleep(75)

                except requests.exceptions.ConnectionError as err:
                    print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "sleeping 60 secs."))
                    time.sleep(60)

                except urllib3.exceptions.ProtocolError as err:
                    print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "sleeping 60 secs."))
                    time.sleep(60)

                except http.client.RemoteDisconnected as err:
                    print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "sleeping 60 secs."))
                    time.sleep(60)

                except ConnectionResetError as err:
                    print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "sleeping 60 secs."))
                    time.sleep(60)

            print(f"[{datetime.datetime.now()}] list:", list)


            if list.meta["result_count"] != 0:
                #Iterating through media in the list to find videos.
                for tweet in list.data:

                    errType = None
                    responding = False
                    while not responding:

                        try:
                            #Getting the tweet's media
                            response = self.client.get_tweet(tweet.id,
                                expansions="attachments.media_keys")
                            media = response.includes

                            status = self.api.get_status(tweet.id)

                            responding = True

                        except tweepy.errors.NotFound as err:
                            print(f"[{datetime.datetime.now()}] Caught error:",
                                f"{err}")
                            errType = type(err)
                            responding = True

                        except tweepy.errors.TwitterServerError as err:
                            print(f"[{datetime.datetime.now()}] Caught error:",
                                f"{err}, sleeping 60 secs")
                            print(type(err))
                            time.sleep(60)

                        except tweepy.errors.TweepyException as err:
                            print(f"[{datetime.datetime.now()}] Caught error:",
                                f"{err}, sleeping 60 secs")
                            print(type(err))
                            time.sleep(60)

                        except requests.exceptions.ConnectionError as err:
                            print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                                "sleeping 60 secs."))
                            time.sleep(60)

                        except urllib3.exceptions.ProtocolError as err:
                            print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                                "sleeping 60 secs."))
                            time.sleep(60)

                        except http.client.RemoteDisconnected as err:
                            print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                                "sleeping 60 secs."))
                            time.sleep(60)

                        except ConnectionResetError as err:
                            print(print(f"[{datetime.datetime.now()}] Caught: {err}",
                                "sleeping 60 secs."))
                            time.sleep(60)

                    if errType == tweepy.errors.NotFound:
                        continue


                    #Finding out if there is a video attached to the tweet
                    if media != {} and media["media"][0].type == "video":

                        #Creating a hash of the video.
                        url = (f"https://twitter.com/"
                            f"{status.author.screen_name}/status/{tweet.id}")

                        try:
                            self.videoHash(url)

                        except videohash.exceptions.DownloadFailed as err:
                            print(f"[{datetime.datetime.now()}] Caught: {err}",
                                "continuing.")
                            continue

                        except videohash.exceptions.FFmpegFailedToExtractFrames as err:

                            print(f"[{datetime.datetime.now()}] Caught: {err}",
                                "continuing.")
                            continue

                        #Searching the database to see if this video already
                        #exists.
                        result = mongoServe().entryCheck(tweet.id, self.videoHashHex,
                            self.videoHashDec)

                        if result != "preexist":
                            #Creating a "post" object.
                            class post:

                                hashDec = self.videoHashDec
                                hashHex = self.videoHashHex
                                platform = "twitter"
                                id = str(tweet.id)
                                author = status.author.screen_name
                                text = status.text
                                timestamp = time.time()
                                uTime = datetime.datetime.timestamp(
                                    status.created_at)


                        #Adding the new tweet to an existing entry
                        if result != None and result != "preexist":

                            post.index = result["index"]
                            mongoServe().addToEntry(post)

                        #Creating a new entry for a new tweet.
                        elif result == None:

                            mongoServe().newEntry(post)

    #---------------------------------------------------------------------------
    def findTelUsers(self, outlinks, lists):

        """
        Desc: Finds new users in the outlinks of telegram posts.
        """

        print(f"[{datetime.datetime.now()}] findTelUsers()")

        for link in outlinks:

            if link.find("https://t.me/s/") != -1:
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


            if username not in lists["telegram"]:
                print(f"[{datetime.datetime.now()}] {username} added.")
                mongoServe().appendLists("telegram", username)
                lists["telegram"].append(username)
        
        return lists

    #---------------------------------------------------------------------------
    def resolve(self, post, hashHex, hashDec):

        """
        Desc: Resolves the post with the database
        """

        #Searching the database to see if this video already
        #exists.
        result = mongoServe().entryCheck(post.id, post.author,
            hashHex,
            hashDec)


        #Adding the new tweet to an existing entry
        if result != None and result != "preexist":

            post.index = result["index"]
            mongoServe().addToEntry(post)

        #Creating a new entry for a new tweet.
        elif result == None:

            mongoServe().newEntry(post)
    

    #---------------------------------------------------------------------------
    def videoHash(self, url):

        """
        Desc: Hashes videos for storage or comparison.
        
        Input:
            - url: The url of the video that needs to be hashed, can include
            any website.

        Output:
            - self.videoHashHex: The Hexadecimal version of the hash
            - self.videoHashDec: The Decimal version of the hash
        """

        #Creating the hash and storing the Hex and Decimal
        vHash = videohash.VideoHash(url=url, frame_interval=12)
        self.videoHashHex = vHash.hash_hex
        self.videoHashDec = int(self.videoHashHex, 16)

        #Garbage collection: removing the video from temporary storage so we
        #don't fill it up.
        videoPath = vHash.storage_path
        cutPath = videoPath[:videoPath.find("temp_storage_dir")]

        shutil.rmtree(cutPath)

        return self.videoHashHex, self.videoHashDec


if __name__ == "__main__":
    #Backing up the database on startup
    #mongoServe().fullBackup()
    lastBackup = time.time()
    running = True
    while running:

        if (lastBackup + 3600) < time.time():
            #mongoServe().fullBackup()
            lastBackup = time.time()

        main().telegram()
