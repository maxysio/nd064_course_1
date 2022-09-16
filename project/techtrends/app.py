import sqlite3
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from logging.config import dictConfig
from flask.logging import default_handler

connectionCount = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connectionCount
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connectionCount += 1    
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post


# Logging
logger = logging.getLogger("__name__")

logging.basicConfig(level=logging.DEBUG)

format = logging.Formatter("%(levelname)s:%(module)s:%(asctime)s, %(message)s", "%m/%d/%Y %H:%M:%S")

debugHandler = logging.StreamHandler(sys.stdout)
debugHandler.setLevel(logging.DEBUG)
debugHandler.setFormatter(format)

logger.addHandler(debugHandler)

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

app.logger.propagate = False
logger.propagate = False

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logger.error('Unable to retrieve article for post id "%s"', post_id)
        return render_template('404.html'), 404
    else:
        logger.info('Article "%s" retrieved!', post['title'])
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('"About Us" page retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            logger.info('New article "%s" created!', title)
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthz endpoint
@app.route('/healthz')
def healthz():
    return {"result": "OK - healthy"}, 200

# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    allPosts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    postCount = len(allPosts)

    return {"db_connection_count": connectionCount, "post_count": postCount}, 200


# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')