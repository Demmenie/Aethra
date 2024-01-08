#07/01/24
#Chico Demmenie
#Aethra/Crawler/dbAccess

import os
import json
import copy
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy

class dbAccess:

    def __init__(self):

        keyFile = open("../data/keys.json", "r")
        self.keys = json.loads(keyFile.read())
        keyFile.close()

        self.connector = self.connect_with_connector()


    def connect_with_connector(self) -> sqlalchemy.engine.base.Engine:
        """
        Initializes a connection pool for a Cloud SQL instance of Postgres.

        Uses the Cloud SQL Python Connector package.
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
    

    #A function that checks if the vehicle already exists.
    #---------------------------------------------------------------------------
    def entryCheck(self, id, author, hashDec, hashHex):

        """
        Desc: Checks any entry against the database to see if the entry already
        exists.
        
        Input:
            - self
            - id
            - hashHex
            - HashDec

        Returns:
            - Result:
                - None (Means it isn't in the database),
                - "preexist" (Means that post has already been entered before)
                - Video object (Means that the video has been seen before but 
                    the post hasn't been entered yet.)
        """

        print(f"[{datetime.datetime.now()}] entryCheck()")

        #COnnect to the database
        conn = self.connector.connect()

        #Looking for videos that match the Hash
        results = conn.execute(
            sqlalchemy.text(f"SELECT * FROM videos WHERE hashHex='{hashHex}'"))
        
        conn.close()

        result = None
        for video in results.fetchall():

            if video[3] == hashHex:
                result = copy.copy(video)

        return result
    

    #---------------------------------------------------------------------------
    def newEntry(self, post):

        """
        Desc: Creates a new video entry.
        
        Input:
            - self
            - post (An object describing the post that needs to be entered.)
        
        Output:
            - Adds a new video object to the database 
        """

        print(f"[{datetime.datetime.now()}] newEntry()")


if __name__ == "__main__":

    print(f"result: {dbAccess().entryCheck(None, None, 1, '1')}")