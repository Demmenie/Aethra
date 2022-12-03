//22/11/2022
//Aethra/web/static/organise.js
//Chico Demmenie

function organise(tweetID, tagName){

  twttr.ready(() => {

    const postDisplay = document.getElementById(
      tagName).getElementsByClassName("display")[0]
    console.log(tweetID)

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
      ).then( function( el ) {
        console.log('Tweet added.');
    });
  });
}
