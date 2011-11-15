import flask
from flask import Flask, g, abort, flash, redirect, url_for, request, render_template
import flaskext.redis 
import datetime
import sys
import os
import secret_key
import yaml

app = Flask(__name__)
app.secret_key = secret_key.key

db = flaskext.redis.init_redis(app)

def get_date():
    today = request.args.get('date', '')
    try:
        datetime.datetime.strptime(today, '%Y-%m-%d')
    except:
        if len(today) > 0:
            flash("Format of date '%s' is incorrect, should be YYYY-mm-dd" % (today,))
        today = datetime.datetime.now().strftime('%Y-%m-%d')
    return today

def get_fixture_data():
    with open("fixture.yaml", "r") as f: 
        return yaml.load(f.read())

@app.route("/setup-first")
def setup_first():
    """Set up a starting dataset.
    """
    fixture = get_fixture_data()
    for c in fixture['circles']:
        did_add = db.sadd('circles', c['mnemonic'])
        if did_add:
            circle_key = 'circle:%s' % c['mnemonic']
            db.hset(circle_key, 'id', c['id'])
            db.hset(circle_key, 'name', c['name'])
            db.hset(circle_key, 'mnemonic', c['mnemonic'])
    
    for p in fixture['people']:
        db.sadd('nicks', p)
    
    db.save()

    flash('First! Database is go \'enna!')

    return redirect(url_for('index'))

@app.route('/')
def index():
    """GUI to state which people are in attendance tonight.
    """
    circles = []
    for mnemonic in db.smembers('circles'):
        circle = dict(
            name= db.hget('circle:%s' % mnemonic, 'name'),
            mnemonic= mnemonic
        )
        circles.append(circle)
    if len(circles) == 0:
        return redirect(url_for('setup_first'))

    people = db.smembers('nicks')
    today = get_date()
    members = []
    for person in people:
        otherkey = '%s:%s' % (person, today)
        circle = db.get(otherkey) or ''
        members.append(dict(name=person, circle=circle))
    
    reports = set()
    for candidate_month in db.keys('meetups:*'):
        junk, _, month = candidate_month.partition(":")
        reports.add(month)
    
    return render_template('index.html', today=today, members=members, circles=circles, reports=reports)

def person_should_be_added(nick, today, circle):
    if not nick and circle:
        return False
    # Has this Nick been registered in a circle today? If so, return False
    for circle_name in db.keys("circle:*:%s" % today):
        if nick in db.smembers(circle_name):
            return False
    return True

@app.route("/attend")
def attend():
    """Ajax callback to record a person as attending a circle.
    """
    today = get_date()
    this_month = today[0:-3]
    nick = request.args.get("nick", "")
    circle = request.args.get("circle", "")
    if person_should_be_added(nick, today, circle):
        key = "circle:%s:%s" % (circle, today)
        db.sadd(key, nick)
        otherkey = "%s:%s" % (nick, today)
        db.set(otherkey, circle)
        
        # Meetup dates are added incrementally
        db.sadd("meetups", today)
        db.sadd("meetups:%s" % this_month, today)
        db.sadd("circles:%s" % this_month, circle)
        return '1'
    return '0'

@app.route("/unattend")
def unattend():
    """Ajax callback to cancel attendance for one person.
    """
    today = get_date()
    this_month = today[0:-3]
    nick = request.args.get("nick")
    circle = request.args.get("circle")
    if nick and circle:
        db.srem("circle:%s:%s" % (circle, today), nick)
        db.delete("%s:%s" % (nick, today))
        return '1'
    return '0'

@app.route("/join")
def join_forskningsavdelningen():
    """Add given nick to the database.
    """
    nick = request.args.get("nick", "")
    message = "Hm, what?"
    if nick:
        db.sadd("nicks", nick)
        message = "Tack, tillagd."
    flash(message)
    return redirect(url_for('index'))
    
        
@app.route("/report")
def report_one_month():
    """Render a monthly report of attendance of the circles.
    """

    def get_circles():
        return db.smembers("circles")
    report = []
    
    chosen_month = request.args.get("month", datetime.datetime.now().strftime('%Y-%m'))
    
    dates_this_month = db.smembers("meetups:%s" % chosen_month)
    circles_this_month = db.smembers("circles:%s" % chosen_month)
    
    for iso_day in sorted(dates_this_month):
        day = {'date': iso_day, 'circles': []}
        for circle_name in circles_this_month:
            circle = {'name': circle_name, 'attendees': []}
            for nick in db.smembers("circle:%s:%s" % (circle_name, iso_day)):
                circle['attendees'].append(nick)
            day['circles'].append(circle)
        report.append(day)
    return render_template('report.html', report=report)

if __name__ == "__main__":
    if 'debug' in sys.argv:
        app.debug = True;

    app.run()
