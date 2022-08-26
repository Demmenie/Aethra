//03/08/2022
//Aethra/web/organise.js
//Chico Demmenie

function organise(tweetList){

  if (tweetList === "None"){
      var p = document.createElement('p');
      p.id = 'text';
      p.innerHTML = "Sorry, we haven't seen that video anywhere before."

      document.getElementById("tweet-container").appendChild(p);
    } else {
      tweetList = JSON.parse(tweetList.replaceAll("'", '"'));

        twttr.ready(() => {
            for (let i = 0; i < tweetList.length; i++) {

              var newDiv = document.createElement('div');
              newDiv.id = `video-${i}`;

              document.getElementById("tweet-container").appendChild(newDiv);

              var tweetID = tweetList[i]["url"].match(/\/(?<tweetID>[0-99999999999999999999]){1,20}$/);
              console.log(tweetID[0].slice(1));

              twttr.widgets.createTweet(
                tweetID[0].slice(1),
                //tweetList[i]["url"],
                document.getElementById(`video-${i}`),
                omit_script=true,
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
        })
    }
  }
