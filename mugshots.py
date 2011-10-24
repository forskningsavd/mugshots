import flask
from flask import Flask, g, abort, flash, redirect, url_for, request, render_template
import flaskext.redis 
import datetime

app = Flask(__name__)
with open('secret_key.txt') as f:
    app.secret_key = f.read()

db = flaskext.redis.init_redis(app)



@app.route("/setup-first")
def setup_first():
    """Set up a starting dataset.
    """
    circles = [
        dict(id=1, name="Software", mnemonic="software"),
        dict(id=2, name="Hardware", mnemonic="hardware")
    ]
    for c in circles:
        did_add = db.sadd('circles', c['mnemonic'])
        if did_add:
            circle_key = 'circle:%s' % c['mnemonic']
            db.hset(circle_key, 'id', c['id'])
            db.hset(circle_key, 'name', c['name'])
            db.hset(circle_key, 'mnemonic', c['mnemonic'])
    
    people = [
        'olleolleolle',
        'jonasb',
        'qzio',
        'phrst',
        'lakevalley',
        'stg',
        'pipeunderscoreslash'
    ]
    for p in people:
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
    people = db.smembers('nicks')
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    members = []
    for person in people:
        otherkey = '%s:%s' % (person, today)
        circle = db.get(otherkey) or ''
        members.append(dict(name=person, circle=circle))
    return render_template('index.html', members=members, circles=circles)

@app.route("/attend")
def attend():
    """Ajax callback to record a person as attending a circle.
    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    this_month = datetime.datetime.now().strftime('%Y-%m')
    nick = request.args.get("nick", "")
    circle = request.args.get("circle", "")
    if nick and circle:
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
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    this_month = today[len(today)-3]
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
    if nick:
        db.sadd("nicks", nick)
        return '1'
    return '0'
        
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
    
    for iso_day in dates_this_month:
        day = {'date': iso_day, 'circles': []}
        for circle_name in circles_this_month:
            circle = {'name': circle_name, 'attendees': []}
            for nick in db.smembers("circle:%s:%s" % (circle_name, iso_day)):
                circle['attendees'].append(nick)
            day['circles'].append(circle)
        report.append(day)
    return render_template('report.html', report=report)

if __name__ == "__main__":
    app.run()
