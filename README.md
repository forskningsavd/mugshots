# mugshots.py

Flask app to note attendance at a Studiecirkel.

## Requirements 

Python, Flask, Redis

    pip install Flask
    pip install Flask-Redis

## Use Flask

Now using a template and a CSS and a favicon, and Jinja template language.

Start by e.g.

    python mugshots.py

## Setup

Initialize the secret key

    head -c 24 /dev/random | base64 > secret_key.txt

Open the page `/setup-first` to populate the database.

## Redis

Run this command in `redis-cli` to reset the database:

    flushdb

## Reporting

The primary feature is the /report.

