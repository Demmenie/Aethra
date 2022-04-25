# Aethra
A tool used to do reverse video searches.

The plan for this search engine is to create a scraper that crawls the open internet looking for videos that it then indexes by creating a locality sensitive hash. The search engine will then allow a person to enter a video that they want to find. This video is then also hashed and compared to what's already in the index, a list of similar videos will then appear with the sources that produced them.
