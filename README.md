# mugshots.py

Flask app to note attendance at a Studiecirkel.

## Requirements 

Python, Flask, Redis

    pip install Flask
    pip install Flask-Redis

## Use Flask

Now using a template and a CSS and a favicon, and Jinja template language.

Start by e.g.

    python mugshots.py debug

## Setup

Initialize the secret key

    head -c 24 /dev/random | base64 > secret_key.txt

The database will be initialized when opening the index page the first time.

## Redis

Run this command in `redis-cli` to reset the database:

    flushdb

## Reporting

The primary feature is the /report.

