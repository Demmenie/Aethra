//30/08/2022
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
      tweetList = JSON.parse(tweetList.replaceAll("'", '"'));

        twttr.ready(() => {
            for (let vid = 0; vid < tweetList.length; vid++) {

              //Creating a new div for each video in the list.
              var newVidDiv = document.createElement('div');
              var br = document.createElement('br');
              newVidDiv.id = `video-${vid}`;
              newVidDiv.className = "video";

              document.getElementById("tweet-container").appendChild(newVidDiv);
              document.getElementById("tweet-container").appendChild(br);


              //Adding each post for each video.
              for (let post = 0; post < tweetList[vid]["postList"].length; post++){

                //A new element for each post.
                var newPostSpan = document.createElement('span');
                newPostSpan.id = `post-${post}`;
                newPostSpan.className = "post";

                newVidDiv.appendChild(newPostSpan);

                //Finding the TweetID
                var url = tweetList[vid]["postList"][post]["url"];
                var tweetID = url.match(/\/(?<tweetID>[0-99999999999999999999]){1,20}$/);
                console.log(tweetID[0].slice(1));

                //Creating the tweet embed with embed factory.
                twttr.widgets.createTweet(
                  tweetID[0].slice(1),
                  //tweetList[i]["url"],
                  newPostSpan,
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
              }
          }
        })
    }
  }
