from flask import Flask, render_template, url_for
import sys
import os



# creates a Flask application, named app
app = Flask(__name__)

# a route where we will display a welcome message via an HTML template

print(os.getcwd())
@app.route("/")
def index():
    return render_template("todaytrade.html")

#run the application freezza prima di inviare a pythonanywhere
if __name__ == "__main__":
    app.run(debug=True)