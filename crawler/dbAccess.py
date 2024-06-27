#07/01/24
#Chico Demmenie
#Aethra/Crawler/dbAccess

import os
import json
import copy
import uuid
import datetime
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
    def entryCheck(self, id, author, hashHex):

        """
        Desc: Checks any entry against the database to see if the entry already
        exists.
        
        Input:
            - self
            - id
            - author
            - hashHex

        Returns:
            - Result:
                - None (Means it isn't in the database),
                - "preexist" (Means that post has already been entered before)
                - Video tuple (Means that the video has been seen before but 
                    the post hasn't been entered yet.)
        """

        print(f"[{datetime.datetime.now()}] entryCheck()")

        #Connecting to the database.
        self.conn = self.connector.connect()

        #Looking for the post in the database.
        post = self.conn.execute(
            sqlalchemy.text(
                f"SELECT * FROM posts WHERE author='{author}' AND "+
                f"postID='{id}'"
            )
        ).fetchone()
        
        #If the post is already there then return "preexist"
        if post != None:
            self.conn.close()
            return "preexist"
        
        #If the post isn't already there then we look for hte video itself.
        else:

            #Looking for videos that match the Hash
            result = self.conn.execute(
                sqlalchemy.text(
                    f"SELECT * FROM videos WHERE hashHex='{hashHex}'"
                )
            ).fetchone()

            self.conn.close()
            
            #If the video isn't there we'll get "None", if it is we return the
            #object.
            return result
    

    #---------------------------------------------------------------------------
    def newVid(self, post):

        """
        Desc: Creates a new video entry.
        
        Input:
            - self
            - post (An object describing the post that needs to be entered.)


        OutPut:
            - vidID
            - postID
        """

        print(f"[{datetime.datetime.now()}] newEntry()")

        #Connect to the database
        self.conn = self.connector.connect()

        #Finding the nearest entry that has a hashDec less than our post.
        vidPlaceBottom = self.conn.execute(
            sqlalchemy.text(
                "SELECT index, MAX(hashDec) FROM videos "+
                f"WHERE hashDec < {post.hashDec}"
            )
        ).fetchone()

        #Finding the nearest entry that has a hashDec more than our post.
        vidPlaceTop = self.conn.execute(
            sqlalchemy.text(
                "SELECT index, MIN(hashDec) FROM videos "+
                f"WHERE hashDec > {post.hashDec}"
            )
        ).fetchone()

        #Checking that the two posts are next to each other.
        if vidPlaceBottom[0] == (vidPlaceTop[0] - 1):
            
            #Updating all of the videos above this one so that the index
            #increases by one.
            self.conn.execute(
                sqlalchemy.text(
                    "UPDATE videos "+
                    "SET index = index + 1 "+
                    f"WHERE index >= {vidPlaceTop[0]}"
                )
            )
            self.conn.commit()

            #Adding the new video to the "videos" table.
            vidID = uuid.uuid4()
            
            self.conn.execute(
                sqlalchemy.text(
                    "INSERT INTO videos "+
                    f"VALUES ({vidPlaceTop[0]}, {vidID}, {str(post.hashDec)}, "+
                    f"{post.hashHex})"
                )
            )
            self.conn.commit()

            self.conn.close()

            #Adding the post to the "posts" table.
            postID = self.addPost(post, vidID)

            return vidID, postID


    #---------------------------------------------------------------------------
    def addPost(self, post, vidID):
        """
        Desc: adds a new post to the "posts" table.

        Input:
            - self
            - post
            - vidID

        Output:
            - postID
        """

        #Connecting to the database.
        self.conn = self.connector.connect()

        #Creating a new id for this post.
        postID = uuid.uuid4()

        #Finding the max index.
        maxPostIndex = self.conn.execute(
            sqlalchemy.text(
                "SELECT MAX(index) FROM videos"
            )
        ).fetchone()

        #Adding the new post to the "posts" table.
        self.conn.execute(
            sqlalchemy.text(
                "INSERT INTO posts "+
                f"VALUES ({(maxPostIndex[0] + 1)}, {vidID}, "+
                f"{post['platform']}, {postID}, {post['author']}, "+
                f"{post['text']}, {post['timestamp']}, {post['uploadTime']})"
            )
        )
        
        #Closing the connection.
        self.conn.commit()
        self.conn.close()

        return postID


if __name__ == "__main__":

    post = {
        "platform": "telegram",
        "id": "1",
        "author": "jimbob",
        "text": "hello",
        "timestamp": 2,
        "uploadTime": 1
        }

    #print(dbAccess().entryCheck(1, "mr.fox", 1))
    print(dbAccess().addPost(post, uuid.UUID("b21faea0-adbe-11ee-abe9-42010a2da002")))