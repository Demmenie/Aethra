#16/07/2024
#Chico Demmenie
#Aethra/crawler/telegram.py

import snscrape
from snscrape.modules import telegram as tg
import datetime
import random
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

        self.maxUsers = self.dba.getMaxTelUsers()


    #---------------------------------------------------------------------------
    def main(self):

        """
        Desc: Saves videos from telegram channels.
        """

        #Going through the channel list to find new posts to add to the database.
        for userIndex in range(0, self.maxUsers):

            channel = self.dba.getTelUser(userIndex)[1]

            try:
                print(f"[{datetime.datetime.now()}] Getting current posts from",
                        channel, userIndex)
                posts = tg.TelegramChannelScraper(channel).get_items()

            except snscrape.base.ScraperException as err:
                print(f"[{datetime.datetime.now()}] Caught: {err}",
                        "continuing.")
                continue

            for index, post in enumerate(posts):
                
                if index > 10:
                    break

                self.utils.resolve(channel, post)

                    


    #---------------------------------------------------------------------------
    def history(self):

        """
        Desc: Saves videos from telegram channels.
        """

        chosenIndex = random.randint(0, self.maxUsers)
        channel = self.dba.getTelUser(chosenIndex)

        try:
            print(f"[{datetime.datetime.now()}] Getting historical posts", 
                    f"from {channel}")
            posts = tg.TelegramChannelScraper(channel).get_items()

        except snscrape.base.ScraperException as err:
            print(f"[{datetime.datetime.now()}] Caught: {err}",
                    "continuing.")

        for post in posts:
            
            self.utils.resolve(channel, post)


if __name__ == "__main__":
    telegram = telegram()

    if input("Main or History? ") in ["m", "M"]:

        while True:
            telegram.main()
    
    else:
        while True:
            telegram.history()