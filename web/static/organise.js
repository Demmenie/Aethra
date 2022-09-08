//09/09/2022
//Aethra/web/organise.js
//Chico Demmenie

function organise(tweetList){

  //If the search returned "None" then we need to display a message to the user.
  if (tweetList === "None"){
      var p = document.createElement('p');
      p.id = 'text';
      p.innerHTML = "Sorry, we haven't seen that video anywhere before."

      document.getElementById("tweet-container").appendChild(p);
    } else {

      //Converting the list on the html page into a json parseable list.
      tweetList = JSON.parse(tweetList);

        twttr.ready(() => {
            for (let vid = 0; vid < tweetList.length; vid++) {

              //Creating a new div for each video in the list.
              var newVidDiv = document.createElement('div');
              var br = document.createElement('br');
              newVidDiv.id = `video-${vid}`;
              newVidDiv.className = "video";

              //Creating a div for the timeline above each post.
              var newTimelineDiv = document.createElement('div');
              newTimelineDiv.id = `timeline-${vid}`;
              newTimelineDiv.className = "timeline";
              newVidDiv.appendChild(newTimelineDiv);

              //Adding all the elements to the document.
              document.getElementById("tweet-container").appendChild(newVidDiv);
              document.getElementById("tweet-container").appendChild(br);

              //Adding each post for each video.
              for (let post = 0; post < tweetList[vid]["postList"].length;
                post++){

                //A new element for each post.
                var newPostSpan = document.createElement('span');
                newPostSpan.id = `post-${post}`;
                newPostSpan.className = "post";

                newVidDiv.appendChild(newPostSpan);

                var postDisplay = document.createElement('div');
                postDisplay.id = "display";
                newPostSpan.appendChild(postDisplay);

                //Adding the upload datetime to the post.
                var uTime = tweetList[vid]["postList"][post]["uploadTime"];
                var date = new Date(uTime * 1000).toUTCString();

                var uDatetime = document.createElement('p');
                uDatetime.innerHTML = date;
                uDatetime.id = "datetime";
                uDatetime.className = "meta";
                postDisplay.appendChild(uDatetime);

                //Finding the TweetID
                var tweetID = tweetList[vid]["postList"][post]["id"];

                //Creating the tweet embed with embed factory.
                twttr.widgets.createTweet(
                  tweetID,
                  postDisplay,
                  omit_script=true,
                  align="left",
                  width=550,
                  dnt=true,
                  {
                    conversation: 'none',
                    align: 'center',
                    theme: 'dark'
                    }
                  )
                  .then( function( el ) {
                    console.log('Tweet added.');
                });

                var metaDiv = document.createElement('div');
                metaDiv.className = "meta";
                newPostSpan.appendChild(metaDiv);

                var author = document.createElement('p');
                author.innerHTML = "Author: @" +
                  tweetList[vid]["postList"][post]["author"];
                author.id = "author";
                author.className = "meta";
                metaDiv.appendChild(author);

                var text = document.createElement('p');
                text.innerHTML = "Caption: " +
                  tweetList[vid]["postList"][post]["text"];
                text.id = "caption";
                text.className = "meta";
                metaDiv.appendChild(text);
              }
          }
        })
    }
  }
