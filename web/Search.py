#07/06/2022
#Chico Demmenie
#Aethra/web/Search.py

from flask import Flask, render_template, send_file
from flask import request, redirect, session

#Defining the flask app
app = Flask(__name__)


#This returns the main page of the flask app
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/q', methods=["POST"])
def sQuery():

    query = request.form['search']
    return redirect(f'/search?q={query}')


@app.route('/search', methods=["GET", "POST"])
def search():

    query = request.args.get('q')
    print(query)
    return render_template('search.html', searchTerm=query)


@app.route('/favicon.ico')
def favicon():
    favi = 'favicon.ico'
    return send_file(favi, mimetype='image/gif')


@app.route('/Icon.png')
def icon():
    icon = 'Icon.png'
    return send_file(icon, mimetype='image/gif')


if __name__ == "__main__":
    app.run(debug=True)
