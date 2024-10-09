#16/07/2024
#Chico Demmenie
#Aethra/crawler/utils.py

from dbAccess import dbAccess
import datetime
import videohash2
import shutil
import time

class utils:

    def __init__(self):

        #Initialising dbAccess
        self.dba = dbAccess()

    
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
        vidLength = None

    
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
        vHash = videohash2.VideoHash(
            url=url,
            frame_interval=12,
            download_worst=True
            )
        videoHashHex = vHash.hash_hex
        videoHashDec = int(videoHashHex, 16)

        videoPath = vHash.storage_path
        cutPath = videoPath[:videoPath.find("/temp_storage_dir")]

        try:
            shutil.rmtree(cutPath)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
            print(cutPath)

        return videoHashHex, videoHashDec
    

    #---------------------------------------------------------------------------
    def resolve(self, channel, post):

        """
        Desc: Resolves if a post should be added to the queue.
        
        Input:
            - post: object from snscrape.
        """

        #First checking for mentioned accounts that we might not have
        #stored yet.
        self.findTelUsers(post.outlinks)

        lastSlash = post.url.rfind('/')
        postID = post.url[lastSlash+1:]
        url = f"https://t.me/{channel}/{postID}?single"

        #Checking to see if the post contains a video.
        try:
            vidLength = videohash2.video_duration(url=url)

        except videohash2.exceptions.DownloadFailed as err:
            print(f"[{datetime.datetime.now()}] Caught: {err}",
                "continuing.")
            return err

        except videohash2.exceptions.FFmpegFailedToExtractFrames as err:
            print(f"[{datetime.datetime.now()}] Caught: {err}",
                "continuing.")
            return err
        
        except UnboundLocalError as err:
            print(f"[{datetime.datetime.now()}] Caught: {err}",
                "continuing.")
            return err
        
        except UnicodeDecodeError as err:
            print(f"[{datetime.datetime.now()}] Caught: {err}",
                "continuing.")
            return err

        if vidLength > 300:
            return "tooLong"
        
        postInQ = self.dba.findQPost("telegram", channel, postID)
        print("Post in Queue:", postInQ)

        if not postInQ:
            postExists = self.dba.postCheck("telegram",
                                            channel, postID)

            if not postExists:

                postOb = self.postOb()
                postOb.platform = "telegram"
                postOb.author = channel
                postOb.id = postID
                postOb.text = post.content
                postOb.timestamp = time.time()
                postOb.uTime = datetime.datetime.timestamp(post.date)
                postOb.vidLength = vidLength

                print(post)

                self.dba.addQPost(postOb)


    #---------------------------------------------------------------------------
    def findTelUsers(self, outlinks):

        """
        Desc: Finds new users in the outlinks of telegram posts.
        """

        print(f"[{datetime.datetime.now()}] findTelUsers()")

        for link in outlinks:

            if link.find("https://t.me/s/+") != -1:
                continue

            elif link.find("https://t.me/+") != -1:
                continue
        
            elif link.find("https://t.me/s/") != -1:
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
            

            userExists = self.dba.findTelUser(username)
            if not userExists:
                print(f"[{datetime.datetime.now()}] {username} added to telegram list.")
                self.dba.addTelUser(username)