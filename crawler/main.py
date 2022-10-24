#05/10/2022
#Chico Demmenie
#Aethra/Scraper/Main.py

import tweepy
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
        self.keys = json.load(open("../data/keys.json", "r"))
        self.lists = open("../data/twitterLists.txt").readlines()

        #Setting up tweepy api (V1.1)
        auth = tweepy.OAuth1UserHandler(
           consumer_key=self.keys["apiKey"],
           consumer_secret=self.keys["apiSecret"],
           access_token=self.keys["accessToken"],
           access_token_secret=self.keys["accessSecret"])

        self.api = tweepy.API(auth)

        #Setting up Tweepy Client (V2.0)
        self.client = tweepy.Client(
            bearer_token=self.keys["bearerToken"],
            consumer_key=self.keys["apiKey"],
            consumer_secret=self.keys["apiSecret"],
            access_token=self.keys["accessToken"],
            access_token_secret=self.keys["accessSecret"],
            wait_on_rate_limit=True)


        #Backing up the database on startup
        mongoServe().fullBackup()
        lastBackup = time.time()
        self.running = True
        while self.running:

            if (lastBackup + 3600) < time.time():
                mongoServe().fullBackup()
                lastBackup = time.time()

            self.twitSave()
            print(f"[{datetime.datetime.now()}] Sleeping 75 secs")
            time.sleep(75)

    #---------------------------------------------------------------------------
    def twitSave(self):

        """
        Desc: Saves videos from Twitter.
        """

        #Going through the lists to find new tweets to add to the database.
        for list in self.lists:

            list = list[:-1]
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
                            print(f"[{datetime.datetime.now()}] Caught: {err},",
                                " continuing.")
                            continue

                        except videohash.exceptions.FFmpegFailedToExtractFrames as err:

                            print(f"[{datetime.datetime.now()}] Caught: {err},",
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


if __name__ == "__main__":
    main()
