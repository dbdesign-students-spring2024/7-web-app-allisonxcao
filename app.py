#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime

from flask import Flask, render_template, request, redirect, url_for, make_response
import pymongo
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv(override=True)  

app = Flask(__name__)


try:
    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("ac10089")]  
    cxn.admin.command("ping")
    print(" * Connected to MongoDB!")
except ConnectionFailure as e:
    print(" * MongoDB connection error:", e)
    sys.exit(1)

@app.route("/")
def home():
    """ Home page route. """
    return render_template("index.html")

@app.route("/read")
def read():
    """ Display posts in a list with links to edit or delete. """
    posts = db.posts.find({}).sort("created_at", -1)
    return render_template("read.html", posts=posts)

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    """ Create a new post about a place to eat. """
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        rating = request.form['rating']

        post = {
            "title": title,
            "description": description,
            "location": location,
            "rating": rating,
        }
        collection.insert_one(post)
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route("/edit/<post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    """ Edit an existing post. """
    post = db.posts.find_one({"_id": ObjectId(post_id)})
    if request.method == 'POST':
        db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {
                "title": request.form['title'],
                "description": request.form['description'],
                "location": request.form['location'],
                "rating": request.form['rating']
            }}
        )
        return redirect(url_for('read'))
    return render_template("edit.html", post=post)

@app.route("/delete/<post_id>", methods=['POST'])
def delete_post(post_id):
    """ Delete a post. """
    db.posts.delete_one({"_id": ObjectId(post_id)})
    return redirect(url_for('read'))

@app.route("/webhook", methods=["POST"])
def webhook():
    """ Handle GitHub webhooks for automated deployment. """
    subprocess.run(["git", "pull"])
    subprocess.run(["chmod", "a+x", "flask.cgi"])
    return make_response("Updated codebase from GitHub.", 200)

@app.errorhandler(Exception)
def handle_error(e):
    """ Handle any exceptions and display them on an error page. """
    return render_template("error.html", error=e)

if __name__ == "__main__":
    app.run(debug=True, load_dotenv=True)