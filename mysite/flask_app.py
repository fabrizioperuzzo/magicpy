from flask import Flask, render_template, url_for, request
import sys
import os
import git

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('https://github.com/fabrizioperuzzo/magicpy.git')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


@app.route("/")
def index():
    return render_template("todaytrade.html")