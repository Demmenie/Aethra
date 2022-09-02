#29/08/2022
#Chico Demmenie
#Aethra/Scraper/Main.py

import tweepy
import time
import datetime
import json
import re
import shutil
import videohash
from MongoAccess import mongoServe


class main:

    """The main class for the scraper"""

    def __init__(self):

        """Initialises the core class functions"""

        #Making sure the Mongo database works.
        #mongoServe()

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


        mongoServe().fullBackup()
        lastBackup = time.time()
        self.running = True
        while self.running:

            if (lastBackup + 3600) < time.time():
                mongoServe().fullBackup()
                lastBackup = time.time()

            self.twitSave()
            print(f"[{datetime.datetime.now()}] Sleeping 60 secs")
            time.sleep(75)

    #---------------------------------------------------------------------------
    def twitSave(self):

        """Saves videos from Twitter."""

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

            print(f"[{datetime.datetime.now()}] list:",
                str(list).encode('utf-8'))


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
                        result = mongoServe().entryCheck(url, self.videoHashHex,
                            self.videoHashDec)

                        #Adding the new tweet to an existing entry
                        if result != None and result != "preexist":
                            mongoServe().addToEntry(result["index"], url,
                            datetime.datetime.timestamp(status.created_at))

                        #Creating a new entry for a new tweet.
                        elif result == None:

                            mongoServe().newEntry(self.videoHashDec,
                                self.videoHashHex, url,
                                datetime.datetime.timestamp(status.created_at))


    #---------------------------------------------------------------------------
    def videoHash(self, url):

        """Hashes videos for storage."""

        vHash = videohash.VideoHash(url=url)
        self.videoHashHex = vHash.hash_hex
        self.videoHashDec = int(self.videoHashHex, 16)

        videoPath = vHash.storage_path
        cutPath = videoPath[:videoPath.find("temp_storage_dir")]

        shutil.rmtree(cutPath)


if __name__ == "__main__":
    main()
