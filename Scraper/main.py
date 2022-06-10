#26/04/2022
#Chico Demmenie
#Aethra/Scraper/Main.py

import tweepy
import json
import re
from videohash import VideoHash
from MongoAccess import mongoServe


class main:

    """The main class for the scraper"""

    def __init__(self):

        """Initialises the core class functions"""

        #Making sure the Mongo database works.
        mongoServe()

        #Retrieving OAuth Twitter keys.
        self.keys = json.load(open("../data/keys.json", "r"))

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


        #Launching the video save for twitter
        self.twitSave()


    #---------------------------------------------------------------------------
    def twitSave(self):

        """Saves videos from Twitter."""

        #Requesting a list of tweets from twitter.
        list = self.client.get_list_tweets("1378399759992512516",
            expansions="attachments.media_keys",
            max_results=5)

        print("List:", list)

        #Iterating through media in the list to find videos.
        for tweet in list.data:

            #Getting the tweet's media
            media = self.client.get_tweet(tweet.id,
                expansions="attachments.media_keys").includes

            #Finding out if there is a video attached to the tweet
            if media != {} and media["media"][0].type == "video":

                #Creating a hash of the video.
                url = f"https://twitter.com/{tweet.author_id}/status/{tweet.id}"

                self.videoHash(url)

                #Searching the database to see if this video already exists.
                result = mongoServe.entryCheck(url, self.videoHashHex)

                if result != None and result != "preexist":
                    mongoServe.addToEntry(result, url, )

                elif result == None and result != "preexist":

                    mongoServe.newEntry()


    #---------------------------------------------------------------------------
    def videoHash(self, url):

        """Hashes videos for storage."""

        self.videoHashHex = VideoHash(url=url).hash_hex
        self.videoHashDec = int(self.videoHashHex, 16)


    #---------------------------------------------------------------------------
    def videoIndex(self):

        """indexes this video in the database."""

        currentCount = mongoServe.docCount()




if __name__ == "__main__":
    main()
