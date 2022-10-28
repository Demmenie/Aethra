/** 10/10/2022
 *  Chico Demmenie
 *  Aethra/web/index.js
 */
const express = require('express');
const path = require('path');
const fs = require('fs');
const morgan = require('morgan');
const pb = require('python-bridge');
const python = pb();

//Getting the search class from python
const sPath = path.join(__dirname, 'search.py')
python.ex`
import importlib.util
import sys
spec = importlib.util.spec_from_file_location("search", ${sPath})
search = importlib.util.module_from_spec(spec)
sys.modules["DBSearch"] = search
spec.loader.exec_module(search)
DBSearch = search.DBSearch()
`


//------------------------------------------------------------------------------
// Initialise server variables
const init = () => {
    //Starting the getList function.
    this.lastUpdate = 0
    this.uList = []
    getList.bind(this)();

    // initialise express app
    this.app = express();
    this.port = 5000;
    this.app.set('view engine', 'ejs');
    this.app.use(express.urlencoded({ extended: true }))
    this.app.use(morgan('combined'))
    server.bind(this)();

    console.log('User connected.');
}


//------------------------------------------------------------------------------
// Server runtime function
const server = () => {
    // listens for activity on root page
    // takes request, response
    this.app.get('/', (req, res) => {
        // Render page
        res.sendFile(path.join(__dirname, "templates/index.html"))
    });

    //Listens listens for the search form to be returned.
    this.app.post('/q', (req, res) => {
        const query = req.body.search

        res.redirect(`/search?q=${query}`)
    })

    //This calls the python search function and returns the completed view.
    this.app.get('/search', (req, res) => {
        /*Calling the cleaning function to make sure that the input is a
        link and not something else.*/
        async function cleaning() {
            return await python`search.DBSearch().cleaning(
                ${req.query.q}
            )`;
        }

        cleaning().then(function(clean){
            //If the input is clean then we'll go look for it.
            if (clean) {
                async function sSearch() {
                    return await python`search.DBSearch().standard(
                        ${req.query.q}, ${this.uList}
                    )`;
                }
                sSearch().then(function(response) {

                    /*If the search returns 'null' then there's nothing to
                    show the user*/
                    if (response == null) {
                        res.render('notFound', {searchTerm: req.query.q})
                    } else {
                        res.render('search',
                        {tweets: response, searchTerm: req.query.q})
                    }
                })

            } else {
                res.redirect(`/url_deny?q=${req.query.q}`)
            }
        })
    })

    /*
    this.app.get('/about', (req, res) => {
        console.log('User has connected to about');

        // Get Data from JSON
        let data = require('./content.json');
        let text = data.about.text;
        let link = data.about.link;

        res.render('index', {letters: text, url: link})
    })
    */

    // Sends a specific page when the search term isn't clean.
    this.app.get('/url_deny', (req, res) => {
        res.render('url_deny', {searchTerm: req.query.q})
    });

    // Returns any document within the 'assets' directory.
    this.app.get(`/assets/*`, (req, res) => {
        const assetPath = path.join(__dirname, req.path);

        // If the file doesn't exist return 404
        try {
            if (fs.existsSync(assetPath)) {
                res.sendFile(assetPath)
            } else {
                send404(req, res)
            }
          } catch(err) {
            send404(req, res);
          }
    });

    // Returns any document within the 'static' directory
    this.app.get(`/static/*`, (req, res) => {
        const assetPath = path.join(__dirname, req.path);

        try {
            if (fs.existsSync(assetPath)) {
                res.sendFile(assetPath)
            } else {
                send404(req, res)
            }
          } catch(err) {
            send404(req, res);
          }
    });

    // Sends any request that isn't recognised before this to the 404 function.
    this.app.get('*', (req, res, next) => {
        send404(req, res);
    });

    // A function that will respond with a 404 error.
    function send404(req, res) {
        // Setting the response code to 404
        res.status(404);
      
        // respond with html page rendered with the correct message
        if (req.accepts('html')) {
            res.render('error', {url: req.url, error: '404: Page not found.',
            text: "Oops! Please try a different page, this one doesn't exist"+
            "...(It's us not you)"});
            return;
        }
      
        // respond with json
        if (req.accepts('json')) {
          res.json({ error: '404: Not found' });
          return;
        }
      
        // default to plain-text
        res.type('txt').send('404: Not found');
    }
    
    // Start listening on the standard port
    this.app.listen(this.port, () => {
        console.log(`Server Listening on port ${this.port}`);
    });
}


/*
//------------------------------------------------------------------------
const isWord = () => {
    const letterJSON = require('./letters.json');
    const monkeyWordArray = letterJSON.letters;

    const loop = () => {
        for(const word of this.wordArray){
            if(word.length >= 2 && word[word.length - 1] == monkeyWordArray[monkeyWordArray.length - 1]){
                let substring = monkeyWordArray.slice(-word.length);

                if(substring.toString().replaceAll(',' , '') == word){
                    letterJSON.words.push(
                        [word, 
                        monkeyWordArray.length - word.length,
                        monkeyWordArray.length - 1]);

                    let data = JSON.stringify(letterJSON);

                    fs.writeFile('./letters.json', data, err => {
                        if (err)
                            console.error(err);
                        else
                            console.log('Monkey made a word')
                    })
                }
            }
        }
        setTimeout(loop, 1000)
    }
    loop()
}
*/

const getList = () => {
    // Retrieves the list of videos from the database every 15 mins
    console.log("Starting getList() loop.")
    loop = () => {
        const time = (new Date().getTime() / 1000)
        if (this.lastUpdate + 900 < time){
            console.log("Updating allDocs / uList.")
            async function refresh(){
                this.uList = await python`search.DBSearch().updateList()`
                this.lastUpdate = (new Date().getTime() / 1000)
                console.log(`Updated uList at ${this.lastUpdate}`)
            }
            refresh(this);
        }
    }
    loop();
}

/*
//------------------------------------------------------------------------
// Get letter and add it too the JSON

const getLetter = () => {
    // Gets a letters, adds it to the current contents of the JSON and then
    // Rewrites the JSON
    loop = () => {
        let letterJSON = require('./letters.json');
        this.Monkey.pickNumber();
        let num = this.Monkey.number

        let char = this.Monkey.typeWriter.keys[num];

        letterJSON.letters.unshift(char);
        let data = JSON.stringify(letterJSON);
        fs.writeFile('letters.json', data, err => {
            if (err)
                console.error(`The monkeys have decided to play with their shit: \n ${err}`);
        });

        setTimeout(loop, 1000);
    }
    loop()
}
*/

init();