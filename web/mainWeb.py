#03/07/2022
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

#Gets the query from the form and redirects to that page.
@app.route('/q', methods=["POST"])
def sQuery():

    query = request.form['search']
    return redirect(f'/search?q={query}')

#Takes the query and does a search based on it.
@app.route('/search', methods=["GET", "POST"])
def search():

    query = request.args.get('q')
    response = DBSearch().standard(query)
    return render_template('search.html', searchTerm=query, tweets=str(response))


@app.route('/favicon.ico')
def favicon():
    favi = 'favicon.ico'
    return send_file(favi, mimetype='image/gif')


@app.route('/Icon.png')
def icon():
    icon = 'Icon.png'
    return send_file(icon, mimetype='image/gif')


@app.route('/<filename>.<extension>')
def pyscript(filename, extension):
    if filename == "pyscript":
        script = f'pyscript/src/pyscript.{extension}'
        return send_file(script)

    elif filename in ["organise", "widgets"]:
        script = f'{filename}.js'
        return send_file(script)

    else:
        return render_template('404.html')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
