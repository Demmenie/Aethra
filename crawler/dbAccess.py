#16/07/2024
#Chico Demmenie
#Aethra/Crawler/dbAccess

import os
import logging
import json
import datetime
import uuid
import time
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy
from sqlalchemy import text


class dbAccess:

    def __init__(self):

        keyFile = open("../data/keys.json", "r")
        self.keys = json.loads(keyFile.read())
        keyFile.close()

        print("Connecting with SQL Database.")
        self.connector = self.connect_with_connector()


    def connect_with_connector(self) -> sqlalchemy.engine.base.Engine:
        """
        Initializes a connection pool for a Cloud SQL instance of Postgres.

        Uses the Cloud SQL Python Connector package.
        """
        # Note: Saving credentials in environment variables is convenient, but
        # not secure - consider a more secure solution such as
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
    

    #A function that checks if the post already exists.
    #---------------------------------------------------------------------------
    def postCheck(self, platform, author, id):

        """
        Desc: Checks any entry against the database to see if the entry already
        exists.
        
        Input:
            - self
            - id
            - author

        Returns:
            - Result:
                - None (Means it isn't in the database),
                - "preexist" (Means that post has already been entered before)
        """

        print(f"[{datetime.datetime.now()}] postCheck()")

        #Connecting to the database.
        self.conn = self.connector.connect()


        #Looking for the post in the database.
        post = self.conn.execute(
            sqlalchemy.text(
                f"SELECT * FROM posts WHERE platform='{platform}' AND "+
                f"author='{author}' AND postID='{id}'"
            )
        ).fetchone()

        self.conn.close()
        
        #If the post is already there then return "preexist"
        if post != None:
            return "preexist"
        
        else:
            return None


    #A function that checks if the video already exists.
    #---------------------------------------------------------------------------
    def vidCheck(self, platform, author, id, hashHex):

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

        print(f"[{datetime.datetime.now()}] vidCheck()")


        #Connecting to the database.
        self.conn = self.connector.connect()

        #Looking for the post in the database.
        post = self.conn.execute(
            sqlalchemy.text(
                f"SELECT * FROM posts WHERE platform='{platform}' AND "+
                f"author='{author}' AND postID='{id}'"
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
        Desc: Checks if the video already exists and creates a new video entry.
        
        Input:
            - self
            - post (An object describing the post that needs to be entered.)
            - hashDec (An integer of the hash)
            - hashHex (A hexadercimal string of the hash)


        OutPut:
            - vidID
            - postIndex
            or
            - "preexist"
        """

        print(f"[{datetime.datetime.now()}] newVid()")


        #Connect to the database
        self.conn = self.connector.connect()

        #Checking that the video isn't already in the DB.
        vidCheck = self.conn.execute(
            sqlalchemy.text(
                "SELECT * FROM videos "+
                f"WHERE hashHex = '{post.hashHex}'"
            )
        ).fetchone()

        if vidCheck != None:
            return "preexist"
        
        else:

            #Finding the nearest entry that has a hashDec less than our post.
            vidPlaceBottom = self.conn.execute(
                sqlalchemy.text(
                    "SELECT index, hashDec "+
                    "FROM videos AS A "+
                    "WHERE hashDec = "+ 
                        "(SELECT MAX(hashDec) "+
                        "FROM videos AS B "+
                        f"WHERE hashDec < {post.hashDec});"
                )
            ).fetchone()

            #Finding the nearest entry that has a hashDec more than our post.
            vidPlaceTop = self.conn.execute(
                sqlalchemy.text(
                    "SELECT index, hashDec "+
                    "FROM videos AS A "+
                    "WHERE hashDec = "+ 
                        "(SELECT MIN(hashDec) "+
                        "FROM videos AS B "+
                        f"WHERE hashDec > {post.hashDec});"
                )
            ).fetchone()


            #If the video is going to the top or bottom of the DB it still needs
            #to know where it's going.
            if vidPlaceTop == None:
                vidPlaceTop = (vidPlaceBottom[0] + 1, )

            elif vidPlaceBottom == None:
                vidPlaceBottom = (vidPlaceTop[0] + 1, )

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

                #Adding the new video to the "videos" table.
                vidID = uuid.uuid4()

                #Adding the new post to the "posts" table.
                stmt = text("INSERT INTO videos VALUES (:index, :id, :hashDec, "+
                            ":hashHex)")
                values = {
                    "index": vidPlaceTop[0],
                    "id": vidID,
                    "hashDec": post.hashDec,
                    "hashHex": post.hashHex
                }
                self.conn.execute(stmt, values)
                self.conn.commit()

                self.conn.close()

                #Adding the post to the "posts" table.
                postIndex = self.addPost(post, vidID)

                return vidID, postIndex
            
            else:
                self.conn.close()
                logging.error("Unable to find adjacent entries.")



    #---------------------------------------------------------------------------
    def addPost(self, post, vidID):
        """
        Desc: adds a new post to the "posts" table.

        Input:
            - self
            - post
            - vidID

        Output:
            - index
        """

        print(f"[{datetime.datetime.now()}] addPost()")

        #Connecting to the database.
        self.conn = self.connector.connect()


        #Finding the max index.
        maxPostIndex = self.conn.execute(
            sqlalchemy.text(
                "SELECT MAX(index) FROM videos"
            )
        ).fetchone()

        postIndex = maxPostIndex[0] + 1
        
        #Adding the new post to the "posts" table.
        stmt = text("INSERT INTO posts VALUES (:index, :vidID, :platform, "+
                    ":postID, :author, :text, :timestamp, :uploadTime)")
        values = {
            "index": postIndex,
            "vidID": vidID,
            "platform": post.platform,
            "postID": post.id,
            "author": post.author,
            "text": post.text,
            "timestamp": post.timestamp,
            "uploadTime": post.uTime
        }
        self.conn.execute(stmt, values)
        
        #Closing the connection.
        self.conn.commit()
        self.conn.close()

        return maxPostIndex
    

    #---------------------------------------------------------------------------
    def addTelUser(self, newUser):

        """
        Desc: Adds a new user to the list of telegram users.

        Input:
            - newUser

        Output:
            - index (The index of the new user in the DB.)
        """

        print(f"[{datetime.datetime.now()}] addTelUser()")

        #Connecting to the database.
        self.conn = self.connector.connect()


        #Finding the max index.
        maxPostIndex = self.conn.execute(
            sqlalchemy.text(
                "SELECT MAX(index) FROM telUsers"
            )
        ).fetchone()

        maxPostIndex = maxPostIndex[0]
        
        #Adding the new post to the "posts" table.
        stmt = text("INSERT INTO telUsers VALUES (:index, :username)")
        values = {
            "index": (maxPostIndex + 1),
            "username": newUser
        }
        self.conn.execute(stmt, values)
        
        #Closing the connection.
        self.conn.commit()
        self.conn.close()

        return maxPostIndex
    

    #---------------------------------------------------------------------------
    def findTelUser(self, username):

        """
        Desc: Looks for a user in the user list.

        Input:
            - Username (String)

        Output:
            - User (Tuple, with index and name)
            - None
        """
    
        print(f"[{datetime.datetime.now()}] findTelUser()")

        #Connecting to the database.
        self.conn = self.connector.connect()


        #Finding the max index.
        search = self.conn.execute(
            sqlalchemy.text(
                "SELECT * FROM telUsers "+
                f"WHERE username = '{username}'"
            )
        ).fetchone()

        self.conn.close()

        return search
        
    
    #---------------------------------------------------------------------------
    def getTelUser(self, index):

        """
        Desc: Looks for a user in the user list.

        Input:
            - Index (Integer)

        Output:
            - User (Tuple, with index and name)
            - None
        """
    
        print(f"[{datetime.datetime.now()}] getTelUser()")

        #Connecting to the database.
        self.conn = self.connector.connect()


        #Finding the max index.
        user = self.conn.execute(
            sqlalchemy.text(
                "SELECT * FROM telUsers "+
                f"WHERE index = '{index}'"
            )
        ).fetchone()

        self.conn.close()

        return user
    

    #---------------------------------------------------------------------------
    def getMaxTelUsers(self):

        """
        Desc: Finds the number of users in the user list

        Output:
            - maxIndex (Integer)
        """
    
        print(f"[{datetime.datetime.now()}] getMaxTelUsers()")

        #Connecting to the database.
        self.conn = self.connector.connect()


        #Finding the max index.
        maxIndex = self.conn.execute(
            sqlalchemy.text(
                "SELECT MAX(index) FROM telUsers "
            )
        ).fetchone()[0]

        self.conn.close()

        return maxIndex
    

    #---------------------------------------------------------------------------
    def getMaxQ(self):

        """
        Desc: Finds the highest Queue index

        Output:
            - maxIndex (Integer)
        """
    
        print(f"[{datetime.datetime.now()}] getMaxQ()")

        #Connecting to the database.
        self.conn = self.connector.connect()

        #Finding the max index.
        maxIndex = self.conn.execute(
            sqlalchemy.text(
                "SELECT MAX(index) FROM queue;"
            )
        ).fetchone()[0]

        self.conn.close()

        if not maxIndex:
            maxIndex = 0
            
        return maxIndex
    

    #---------------------------------------------------------------------------
    def addQPost(self, post):

        """
        Desc: Finds the number of users in the user list

        Output:
            - maxIndex (Integer)
        """
    
        print(f"[{datetime.datetime.now()}] addQPost()")

        index = self.getMaxQ() + 1

        #Connecting to the database.
        self.conn = self.connector.connect()

        #Adding the new post to the "posts" table.
        stmt = text("INSERT INTO queue VALUES (:index, :platform, :postid, "+
                    ":author, :text, :timestamp, :uploadtime, :vidlength);")
        values = {
            "index": index,
            "platform": post.platform,
            "postid": post.id,
            "author": post.author,
            "text": post.text,
            "timestamp": post.timestamp,
            "uploadtime": post.uTime,
            "vidlength": post.vidLength
        }
        self.conn.execute(stmt, values)
        self.conn.commit()

        self.conn.close()


    #---------------------------------------------------------------------------
    def findQPost(self, platform, author, postID):

        """
        Desc: Finds a post in the queue

        Output:
            - post
            - None
        """
    
        print(f"[{datetime.datetime.now()}]  findQPost()")

        #Connecting to the database.
        self.conn = self.connector.connect()

        #Finding the max index.
        post = self.conn.execute(
            sqlalchemy.text(
                "SELECT * FROM queue WHERE "+
                f"platform = '{platform}' AND author = '{author}' AND "+
                f"postid = '{postID}';"
            )
        ).fetchone()

        self.conn.close()

        return post


    #---------------------------------------------------------------------------
    def popQPost(self):

        """
        Desc: Pops the lowest post from the queue. 

        Output:
            - post (tuple)
        """
    
        print(f"[{datetime.datetime.now()}] popQPost()")

        #Connecting to the database.
        self.conn = self.connector.connect()

        #taking the first post
        post = self.conn.execute(
            sqlalchemy.text(
                "SELECT * FROM queue WHERE index = 0"
            )
        ).fetchone()

        #Removing the post we just grabbed
        self.conn.execute(
            sqlalchemy.text(
                "DELETE FROM queue WHERE index = 0;"
            )
        )

        #Updating all of the posts above this one so that the index
        #decreasses by one.
        self.conn.execute(
            sqlalchemy.text(
                "UPDATE queue "+
                "SET index = index - 1 "+
                f"WHERE index > 0"
            )
        )
        self.conn.commit()

        self.conn.close()

        return post