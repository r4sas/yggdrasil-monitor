#!/usr/bin/env python

import signal, sys, time
from functools import wraps
from flask import Flask, Response, render_template
from flask_restful import Resource, Api
import requests
import psycopg2
import json
from config import DB_PASS, DB_USER, DB_NAME, DB_HOST, DB_RETRIES, DB_RECONNIDLE, ALIVE_SECONDS

######

app = Flask(__name__)
api = Api(app)

def pg_connect():
    return psycopg2.connect(host=DB_HOST,\
                              database=DB_NAME,\
                              user=DB_USER,\
                              password=DB_PASS)


# dbconn = pg_connect() # initialize connection


def retry(fn):
    @wraps(fn)
    def wrapper(*args, **kw):
        for x in range(DB_RETRIES):
            try:
                return fn(*args, **kw)
            except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
                print ("\nDatabase Connection [InterfaceError or OperationalError]")
                print ("Idle for %s seconds" % (cls._reconnectIdle))
                time.sleep(DB_RECONNIDLE)
                dbconn = pg_connect()
    return wrapper


def signal_handler(sig, frame):
    dbconn.close()
    sys.exit(0)


def age_calc(ustamp):
    if (time.time() - ustamp) <= ALIVE_SECONDS:
        return True
    else:
        return False


# active nodes
class nodesCurrent(Resource):
    @retry
    def get(self):
        dbconn = pg_connect()
        cur = dbconn.cursor()

        nodes = {}
        cur.execute("select * from yggindex")
        for i in cur.fetchall():
            if age_calc(int(i[2])):
                nodes[i[0]] = [i[1], int(i[2])]

        dbconn.commit()
        cur.close()

        nodeinfo = {}
        nodeinfo['yggnodes'] = nodes

        dbconn.close()
        return nodeinfo


# nodes info
class nodesInfo(Resource):
    @retry
    def get(self):
        dbconn = pg_connect()
        cur = dbconn.cursor()
        nodes = {}
        cur.execute("select * from yggnodeinfo")
        for i in cur.fetchall():
            if age_calc(int(i[2])):
                nodes[i[0]] = json.loads(i[1])

        dbconn.commit()
        cur.close()

        nodeinfo = {}
        nodeinfo['yggnodeinfo'] = nodes

        dbconn.close()
        return nodeinfo


# alive nodes count for latest 24 hours
class nodes24h(Resource):
    @retry
    def get(self):
        dbconn = pg_connect()
        cur = dbconn.cursor()
        nodes = {}
        cur.execute("SELECT * FROM timeseries ORDER BY unixtstamp DESC LIMIT 24")
        for i in cur.fetchall():
            nodes[i[1]] = i[0]

        dbconn.commit()
        cur.close()

        nodeinfo = {}
        nodeinfo['nodes24h'] = nodes

        dbconn.close()
        return nodeinfo


# alive nodes count for latest 30 days
class nodes30d(Resource):
    @retry
    def get(self):
        dbconn = pg_connect()
        cur = dbconn.cursor()
        nodes = {}
        cur.execute("SELECT * FROM timeseries ORDER BY unixtstamp DESC LIMIT 24 * 30")
        for i in cur.fetchall():
            nodes[i[1]] = i[0]

        dbconn.commit()
        cur.close()

        nodeinfo = {}
        nodeinfo['nodes30d'] = nodes

        dbconn.close()
        return nodeinfo


@app.route("/")
@retry
def fpage():
    dbconn = pg_connect()
    cur = dbconn.cursor()
    nodes = 0
    cur.execute("select * from yggindex")

    for i in cur.fetchall():
        if age_calc(int(i[2])):
            nodes += 1

    dbconn.commit()
    cur.close()

    dbconn.close()
    return render_template('index.html', nodes=nodes)

@app.route('/map')
@app.route('/map/network')
def page_network():
    return render_template('map/network.html', page='network')

@app.route('/map/about')
def page_about():
    return render_template('map/about.html', page='about')

@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

# sort out the api request here for the url
api.add_resource(nodesCurrent, '/current')
api.add_resource(nodesInfo, '/nodeinfo')
api.add_resource(nodes24h, '/nodes24h')
api.add_resource(nodes30d, '/nodes30d')

# regirster signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3001)
