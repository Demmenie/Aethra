#16/07/2024
#Chico Demmenie
#Aethra/crawler/utils.py

from dbAccess import dbAccess
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