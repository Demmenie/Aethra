#05/07/2022
#Chico Demmenie
#Aethra/web/mainWeb.py

from flask import Flask, render_template, send_file
from flask import request, redirect, session
from search import DBSearch
import tweepy

#Defining the flask app
app = Flask(__name__)


#This returns the main page of the flask app
@app.route('/')
def index():
    return render_template('index.html')

#Gets the query from the form, cleans it and redirects to that page.
@app.route('/q', methods=["POST"])
def sQuery():

    query = request.form['search']
    cleanQuery = DBSearch().cleaning(query)

    if cleanQuery:
        return redirect(f'/search?q={query}')

    else:
        return redirect('/url_deny')

#Takes the query and does a search based on it.
@app.route('/search', methods=["GET", "POST"])
def search():

    query = request.args.get('q')

    #Doing another input clean due to url not being trustworthy.
    cleanQuery = DBSearch().cleaning(query)

    if not cleanQuery:
        return redirect('/url_deny')

    else:

        response = DBSearch().standard(query)
        print(response)

        if response != None:
            return render_template('search.html', searchTerm=query,
                tweets=str(response))

        else:
            return render_template('notFound.html', searchTerm=query)

#The route used when an input seems malicious
@app.route('/url_deny')
def url_deny():
    return render_template('url_deny.html')


@app.route('/favicon.ico')
def favicon():
    favi = 'webAssets/favicon.ico'
    return send_file(favi, mimetype='image/gif')


@app.route('/<image>.png')
def icon(image):
    icon = f'webAssets/{image}.png'
    return send_file(icon, mimetype='image/gif')


@app.route('/<filename>.js')
def javascript(filename):

    if filename in ["organise", "widgets"]:
        script = f'static/{filename}.js'
        return send_file(script)

    else:
        return render_template('404.html')

@app.errorhandler(404)
def page_not_found(e):
    #Note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    #Note that we set the 404 status explicitly
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)
