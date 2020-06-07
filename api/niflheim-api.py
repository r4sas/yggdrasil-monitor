#!/usr/bin/env python

import signal, sys, time
from flask import Flask, render_template
from flask_restful import Resource, Api
import requests
import psycopg2
import json

######

DB_PASS = "password"
DB_USER = "yggindex"
DB_NAME = "yggindex"
DB_HOST = "localhost"

# count peer alive if it was available not more that amount of seconds ago
# I'm using 1 hour beause of running crawler every 15 minutes
ALIVE_SECONDS = 3600 # 1 hour

######

app = Flask(__name__)
api = Api(app)

dbconn = psycopg2.connect(host=DB_HOST,\
                          database=DB_NAME,\
                          user=DB_USER,\
                          password=DB_PASS)

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
    def get(self):
        cur = dbconn.cursor()
        nodes = {}
        cur.execute("select * from yggindex")
        for i in cur.fetchall():
            if age_calc(int(i[2])):
                nodes[i[0]] = [i[1], int(i[2])]

        dbconn.commit()
        cur.close()

        nodelist = {}
        nodelist['yggnodes'] = nodes

        return nodelist


# nodes info
class nodesInfo(Resource):
    def get(self):
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

        return nodeinfo


# alive nodes count for latest 24 hours
class nodes24h(Resource):
    def get(self):
        cur = dbconn.cursor()
        nodes = {}
        cur.execute("SELECT * FROM timeseries ORDER BY unixtstamp DESC LIMIT 24")
        for i in cur.fetchall():
            nodes[i[1]] = i[0]

        dbconn.commit()
        cur.close()

        nodeinfo = {}
        nodeinfo['nodes24h'] = nodes

        return nodeinfo


# alive nodes count for latest 30 days
class nodes30d(Resource):
    def get(self):
        cur = dbconn.cursor()
        nodes = {}
        cur.execute("SELECT * FROM timeseries ORDER BY unixtstamp DESC LIMIT 24 * 30")
        for i in cur.fetchall():
            nodes[i[1]] = i[0]

        dbconn.commit()
        cur.close()

        nodeinfo = {}
        nodeinfo['nodes30d'] = nodes

        return nodeinfo


# alive nodes count for latest 24 hours
class crawlResult(Resource):
    def get(self):
        with open('api/results.json', 'r') as f:
            data = json.load(f)

        return data


@app.route("/")
def fpage():
    cur = dbconn.cursor()
    nodes = 0
    cur.execute("select * from yggindex")

    for i in cur.fetchall():
        if age_calc(int(i[2])):
            nodes += 1

    dbconn.commit()
    cur.close()

    return render_template('index.html', nodes=nodes)


# sort out the api request here for the url
api.add_resource(nodesCurrent, '/current')
api.add_resource(nodesInfo, '/nodeinfo')
api.add_resource(nodes24h, '/nodes24h')
api.add_resource(nodes30d, '/nodes30d')
api.add_resource(crawlResult, '/result.json')

# regirster signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    app.run(host='::', port=3000)
