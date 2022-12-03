/** 22/11/2022
 *  Chico Demmenie
 *  Aethra/web/index.js
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const morgan = require('morgan');
const pb = require('python-bridge');
const python = pb();
const pageRender = require('./render');

//Getting the search class from python
const sPath = path.join(__dirname, 'search.py');
python.ex`
import importlib.util
import sys
spec = importlib.util.spec_from_file_location("search", ${sPath})
search = importlib.util.module_from_spec(spec)
sys.modules["search"] = search
spec.loader.exec_module(search)
DBSearch = search.DBSearch()
`


//------------------------------------------------------------------------------
// Initialise server variables
const init = () => {
    //Starting the getList function.
    this.lastUpdate = 0;
    this.uList = [];
    getList.bind(this)();

    // initialise express app
    this.app = express();
    this.port = 5000;
    this.app.set('view engine', 'ejs');
    this.app.use(express.urlencoded({ extended: true }));
    this.app.use(morgan('combined'));
    server.bind(this)();

    console.log('User connected.');
}


//------------------------------------------------------------------------------
// Server runtime function
const server = () => {

    
    // =================================
    // listens for activity on root page
    // takes request, response
    this.app.get('/', (req, res) => {
        // Render page
        res.sendFile(path.join(__dirname, "templates/index.html"));
    });

    //Listens listens for the search form to be returned.
    this.app.post('/q', (req, res) => {
        const query = req.body.search;

        res.redirect(`/search?q=${query}`);
    });

    // =================================
    //This calls the python search function and returns the completed view.
    this.app.get('/search', (req, res) => {
        /*Calling the cleaning function to make sure that the input is a
        link and not something else.*/
        async function cleaning() {
            return await python`DBSearch.cleaning(
                ${req.query.q}
            )`;
        }

        cleaning().then(function(clean){
            //If the input is clean then we'll go look for it.
            if (clean) {
                async function sSearch() {
                    return await python`DBSearch.standard(
                        ${req.query.q}, ${this.uList}
                    )`;
                }
                sSearch.bind(this)().then(function(sResponse) {

                    /*If the search returns 'null' then there's nothing to
                    show the user*/
                    if (sResponse == null) {
                        res.render('notFound', {searchTerm: req.query.q});
                    } else if (sResponse == "download_failed"){
                        sendErr(req, res, 500);
                    } else {
                        let page = pageRender(sResponse).toString();
                        page = page.replaceAll(",", "");
                        page = page.replaceAll("**", ",");
                        console.log(page);
                        res.render('search',
                        {page: page,
                            searchTerm: req.query.q});
                    }
                }.bind(pageRender));

            } else {
                res.redirect(`/url_deny?q=${req.query.q}`);
            }
        }.bind(this, pageRender));
    });

    // =================================
    // Returns the about page.
    this.app.get('/about', (req, res) => {
        res.sendFile(path.join(__dirname, "templates/about.html"));
    })

    // =================================
    // Sends a specific page when the search term isn't clean.
    this.app.get('/url_deny', (req, res) => {
        res.render('url_deny', {searchTerm: req.query.q});
    });

    // =================================
    // Returns any document within the 'assets' directory.
    this.app.get(`/assets/*`, (req, res) => {
        const assetPath = path.join(__dirname, req.path);

        // If the file doesn't exist return 404
        try {
            if (fs.existsSync(assetPath)) {
                res.sendFile(assetPath);
            } else {
                send404(req, res, 404);
            }
          } catch(err) {
            sendErr(req, res, 404);
          }
    });

    // =================================
    // Returns any document within the 'static' directory
    this.app.get(`/static/*`, (req, res) => {
        const assetPath = path.join(__dirname, req.path);

        try {
            if (fs.existsSync(assetPath)) {
                res.sendFile(assetPath);
            } else {
                sendErr(req, res, 404);
            }
          } catch(err) {
            sendErr(req, res, 404);
          }
    });

    // =================================
    // Sends any request that isn't recognised before this to the 404 function.
    this.app.get('*', (req, res, next) => {
        const err = 404
        sendErr(req, res, err);
    });

    // =================================
    // A function that will respond with a 404 error.
    function sendErr(req, res, err) {
        // Setting the response code to 404
        res.status(err);

        if (err == 404){
            title = "404: Page doesn't exist";
            text = "Whoops, Wrong page...maybe try a different one?";
        } else if (err == 500){
            title = "500: Server error";
            text = "Oops, something went wrong (It's us not you)..."+
                "maybe try again? 🤷";
        }
      
        // respond with html page rendered with the correct message
        if (req.accepts('html')) {
            res.render('error', {url: req.url, error: title,
            text: text});
            return;
        }
      
        // respond with json
        if (req.accepts('json')) {
          res.json({ error: err });
          return;
        }
      
        // default to plain-text
        res.type('txt').send(err);
    }
    
    // Start listening on the standard port
    this.app.listen(this.port, () => {
        console.log(`Server Listening on port ${this.port}`);
    });
}


// -----------------------------------------------------------------------------
const getList = () => {
    // Retrieves the list of videos from the database every 15 mins
    console.log("Starting getList() loop.");

    // Creating a recurring loop
    loop = async () => {
        const time = (new Date().getTime() / 1000);

        // This should update every 15 mins.
        if ((this.lastUpdate + 900) < time){
            console.log(`Updating allDocs / uList ${this.lastUpdate}`);
            
            // An async function that calls the python function to update
            // Returns this.uList and this.lastUpdate.
            async function refresh(){
                return await python`DBSearch.updateList()`;
            }
            refresh.bind(this)().then(function(uList){
                this.uList = uList
                console.log(`${time}: returned`)
            }.bind(this))

            this.lastUpdate = (new Date().getTime() / 1000);
            console.log(`Updated uList at ${this.lastUpdate}`);
        }
        // console.log(`${time - this.lastUpdate}:`, this.uList);
        setTimeout(loop.bind(this), 1000)
    }
    loop.bind(this)()
}

init();