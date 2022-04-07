#07/04/2022
#Chico Demmenie
#Aethra/Scraper/Main.py

import tweepy
import json
import re


class main:

    """The main class for the scraper"""

    def __init__(self):

        """Initialises the core class functions"""

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
            media = self.api.get_status(tweet.id)


if __name__ == "__main__":
    main()
