//22/11/2022
//Chico Demmenie
//Aethra/web/render.js

const renderer = (list) => {
    
    /* The tweet list that's generated from the search function is passed into 
        this function, which then parses it as JSON.*/
    tweetList = JSON.parse(list);
    let page = []

    // This for loop iterates over every video document in the list.
    for (let vid = 0; vid < tweetList.length; vid++) {
        // We create a timeline for each video.
        page.push(`<div id="video-${vid}" class="video">`)
        page.push(`<div id="timeline">`)

        //Sorting the postList by uploadTime.
        const thisVid = tweetList[vid];
        const postList = thisVid.postList.sort(function(a, b){
            return a.uploadTime - b.uploadTime
        })
        
        // This loop iterated over every post in the postList.
        for (let post = 0; post < postList.length; post++) {
            // Here we're creating an element for each post in this video.
            page.push(`<span id="post-${vid}-${post}" class="post">`)
            page.push('<div class="display">')

            //Adding the upload datetime to the post.
            const uTime = postList[post]["uploadTime"];
            const date = new Date(uTime * 1000).toUTCString();
            const tweetID = postList[post]["id"]
            
            /* Adding the time and calling the Client-side function to display
                the tweet.*/
            page.push(`<p id="datetime" class="meta">${date}</p>`)
            page.push(`<script type="text/javascript">organise("${tweetID}"** "post-${vid}-${post}")</script>`)
            page.push('</div>')

            //Creating a meta div for metadata.
            page.push('<div class="meta">')

            //Showing the author.
            author = postList[post]["author"]
            page.push(`<p id="author" class="meta">
                Author: @${author}</p>`)

            //Showing the caption on the post.
            page.push(`<p id="caption" class="meta">Caption: 
                "${postList[post]["text"]}"</p>`)

            //Creating a link to the original post.
            page.push(`<a href="https://twitter.com/${author}/
                status/${postList[post]["id"]} target="_blank">`)
            page.push('<p id="source" class="meta">Source</p></a>')

            //Closing the meta div and the span
            page.push('</div></span>')
        }

        page.push('</div></div><br>')
    }
    return page
}

module.exports = renderer