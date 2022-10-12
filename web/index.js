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


//------------------------------------------------------------------------
// Initialise server variables
const init = () => {
    // initialise express app
    this.app = express();
    this.port = 5000;
    this.app.set('view engine', 'ejs');
    this.app.use(express.urlencoded({ extended: true }))
    this.app.use(morgan('combined'))
    server.bind(this)();

    console.log('User connected.');
}


//------------------------------------------------------------------------
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
                        ${req.query.q}
                    )`;
                }
                sSearch().then(function(response) {

                    //If the search returns 'null' then there's nothing to show the user
                    if (response == null) {
                        res.render('notFound', {searchTerm: req.query.q})
                    } else {
                        res.render('search', {tweets: response, searchTerm: req.query.q})
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

    this.app.get('/url_deny', (req, res) => {
        // Render page
        res.render('url_deny', {searchTerm: req.query.q})
    });

    const sendFile = (req, res) => {
        const assetsPath = path.join(__dirname, 'assets');
        fs.readdir(assetsPath, (err, assetFiles) => {
            //handling error
            if (err) {
                return console.log('Unable to scan directory: ' + err);
            } 

            //listing all files using forEach
            assetFiles.forEach((file) => {
                this.app.get(`/assets/${file}`, (req, res) => {
                    res.sendFile(path.join(__dirname, `assets/${file}`))
                })
            });
        });

        //Defining paths for files the client needs.
        const staticPath = path.join(__dirname, 'static');
        const CSSPath = path.join(__dirname, 'static/CSS');
        fs.readdir(staticPath, (err, staticFiles) => {
            //handling error
            if (err) {
                return console.log('Unable to scan directory: ' + err);
            } 

            fs.readdir(CSSPath, (err, CSSFiles) => {
                //handling error
                if (err) {
                    return console.log('Unable to scan directory: ' + err);
                } 

                //listing all files using forEach
                staticFiles.forEach((file) => {

                    //This exposes the js files that the client needs.
                    this.app.get(`/static/${file}`, (req, res) => {
                        res.setHeader('content-type', 'text/javascript');
                        res.sendFile(path.join(__dirname, `static/${file}`))
                    })
                    
                    //This exposes all the CSS files.
                    CSSFiles.forEach((file) => {
                        this.app.get(`/static/css/${file}`, (req, res) => {
                            res.sendFile(path.join(__dirname,
                                `static/css/${file}`))
                        })
                    })
                });
            });        
        });
    }
    sendFile();

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