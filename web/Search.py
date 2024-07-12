#08/11/2022
#Chico Demmenie
#Aethra/web/search.py

#Importing dependencies
from operator import itemgetter
import datetime
import videohash
import shutil
import json
import os
import time
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy


class DBSearch:

    """This class contains functions that search the database for the website"""

    def __init__(self):

        """Class initialisation and database connection."""

        #Opening a connection with the MongoDB Atlas Database
        keyFile = open("../data/keys.json", "r")
        self.keys = json.loads(keyFile.read())
        keyFile.close()

        print("Connecting with SQL Database.")
        self.connector = self.connect_with_connector(self.keys)

        #mongoPass = keys["mongoPass"]
        #mongoCluster = keys["mongoCluster"]
        #mongoAccount = keys["mongoAccount"]
        #conn = ''.join(f"mongodb+srv://{mongoAccount}:{mongoPass}"+
        #    f"{mongoCluster}.mongodb.net/{mongoAccount}?retryWrites=true&w="+
        #    "majority")

        #Setting a 5-second connection timeout so that we're not pinging the
        #server endlessly
        #self.client = pymongo.MongoClient(conn,
        #    tls=True,
        #    serverSelectionTimeoutMS=5000)

        #Setting the class wide variables that connect to the database and the
        #video collection.
        #self.db = self.client.Aethra
        #self.video = self.db.video3


    #---------------------------------------------------------------------------
    def connect_with_connector(self, keys) -> sqlalchemy.engine.base.Engine:
        """
        Initializes a connection pool for a Cloud SQL instance of Postgres
        using the Cloud SQL Python Connector package.

        Input:
            - keys

        Output:
            - pool
        """
        # Note: Saving credentials in environment variables is convenient, but not
        # secure - consider a more secure solution such as
        # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
        # keep secrets safe.

        ip_type = IPTypes.PRIVATE if os.environ.get(self.keys["gPrivIP"]) else IPTypes.PUBLIC

        # initialize Cloud SQL Python Connector object
        connector = Connector()

        def getconn() -> pg8000.dbapi.Connection:
            conn: pg8000.dbapi.Connection = connector.connect(
                self.keys["gProj"],
                "pg8000",
                user=self.keys["gUser"],
                password=self.keys["gPass"],
                db=self.keys["gDB"],
                ip_type=ip_type,
            )
            return conn

        # The Cloud SQL Python Connector can be used with SQLAlchemy
        # using the 'creator' argument to 'create_engine'
        pool = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            # ...
        )
        return pool


    #---------------------------------------------------------------------------
    def cleaning(self, query):

        """Cleans up and checks that the query is correct."""

        clean = True
        #First looking to see if it's a website.
        if (query.find("https://", 0, 8) != 0 and
            query.find("http://", 0, 8) != 0):

            clean = False

        #Then looking for character that don't belong in a URL.
        elif query.find(".", 8) < 0 or query.find(".", 8) < 0:  

            clean = False

        else:
            for char in list(query):

                if char not in list("""ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno
                    pqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;="""):

                    clean = False
                    break

        #Returning True or False for if the URL is clean or not.
        return clean


    #---------------------------------------------------------------------------
    def standard(self, url):

        """Searches the database in the standard way using binary search."""

        print(f"[{datetime.datetime.now()}] DBSearch.standard()")

        #Connecting to the database.
        self.conn = self.connector.connect()


        start = time.time()
        #Hashing the video
        try:
            self.videoHash(url)

        #Printing the error if one occurs 
        except videohash.exceptions.DownloadFailed as err:
            print(f"videoHash errored out with exception:\n{err}")
            return "download_failed", err

        print(f"Hashing in {time.time() - start}")
        start = time.time()

        vidList = self.conn.execute(
            sqlalchemy.text(
                "SELECT * FROM "+
                    "((SELECT * FROM videos "+
                    f"WHERE hashDec >= {self.hashDec} "+
                    "ORDER BY hashDec ASC LIMIT 5) "+ 
                    "UNION ALL "+
                    "(SELECT * FROM videos "+
                    f"WHERE hashDec < {self.hashDec} "+
                    "ORDER BY hashDec DESC LIMIT 5)) "+
                "AS nearest "+
                f"ORDER BY abs({self.hashDec} - hashDec) LIMIT 10;"
            )
        )

        #Adding the videos as JSON objects with the associated posts
        if vidList != None:

            returnList = []
            for vid in vidList:

                vidID = vid[1]
                vidOb = {
                    "index": vid[0],
                    "hashHex": vid[3],
                    "hashDec": int(vid[2]),
                    "postList": []
                }

                postList = self.conn.execute(
                    sqlalchemy.text(
                        "SELECT * FROM posts "+
                        f"WHERE vidID = '{vidID}';"
                    )
                )

                for post in postList:
                    postOb = {
                        "platform": post[2],
                        "id": post[3],
                        "author": post[4],
                        "text": post[5],
                        "timestamp": post[6],
                        "uploadTime": post[7]
                    }

                    vidOb["postList"].append(postOb)

                returnList.append(vidOb)


            print(f"Search in {time.time() - start}")
            start = time.time()


            for video in returnList:
                video["sDiff"] = abs(int(video["hashDec"]) - self.hashDec)

            returnList = sorted(returnList, key=itemgetter('sDiff')) 
            print(f"Sorting in {time.time() - start}")

            self.conn.close()

            return json.dumps(returnList)

        else:
            self.conn.close()
            return vidList


    #---------------------------------------------------------------------------
    def entryCount(self):

        """Hashes videos for storage."""

        print(f"[{datetime.datetime.now()}] DBSearch.entryCount()")

        #Connecting to the database.
        self.conn = self.connector.connect()

        vidCount = self.conn.execute(
            sqlalchemy.text(
                "SELECT COUNT(index) FROM videos"
            )
        ).fetchone()

        postCount = self.conn.execute(
            sqlalchemy.text(
                "SELECT COUNT(index) FROM posts"
            )
        ).fetchone()

        self.conn.close()
        return vidCount[0], postCount[0]

    
    #---------------------------------------------------------------------------
    def videoHash(self, url):

        """Hashes videos for storage."""

        #Creating hash, setting variables
        vHash = videohash.VideoHash(url=url, frame_interval=12)
        self.hashHex = vHash.hash_hex
        self.hashDec = int(self.hashHex, 16)

        #After the hash has been found, the temp storage is cleared.
        videoPath = vHash.storage_path
        cutPath = videoPath[:videoPath.find("temp_storage_dir")]

        shutil.rmtree(cutPath)


if __name__ == "__main__":

    print(DBSearch().entryCount())
