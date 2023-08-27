//08/07/2023
//Aethra/web/static/organise.js
//Chico Demmenie

function organise(postID, author, platform, tagName){

  const postDisplay = document.getElementById(
    tagName).getElementsByClassName("display")[0]
  console.log(postID);

  // Creating a telegram embed.
  if (platform == "telegram") {
    br = document.createElement("br");
    postDisplay.append(br);

    tg = document.createElement("script");
    tg.setAttribute("src", "https://telegram.org/js/telegram-widget.js?22");
    tg.setAttribute("data-telegram-post", `${author}/${postID}`);
    tg.setAttribute("data-width", "100%");
    tg.setAttribute("data-userpic", "false");
    tg.setAttribute("data-dark", "1");

    postDisplay.append(tg);

    br = document.createElement("br");
    postDisplay.append(br);


  } else if (platform == "twitter") {

    // Creating the tweet embed with embed factory.
    twttr.ready(() => {
      twttr.widgets.createTweet(
        postID,
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
}
