# Aethra
A tool used to do reverse video searches.

This search engine includes a scraper that crawls the open internet looking for videos that it then indexes by creating a locality sensitive hash of the video. The search engine will then allow a person to enter a video that they want to find. This video is then also hashed and compared to what's already in the index using binary search; a list of similar videos will then appear with the sources that produced them.

Please bear in mind that our database is not exhaustive and we are still expanding our search patterns. We are starting small with just a few sources on Twitter and then slowly expanding our crawler to include other sources of video.

We currently use [this video hashing module](https://github.com/akamhy/videohash), which is far from perfect. There seem to be collisions present in this hashing algorithm and it is also very slow.

This search engine will not yet show longer versions of a video clip; only the same or similar clips of video.

<a href="https://www.buymeacoffee.com/Demmenie" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>
