#!/usr/bin/env python

import time
from flask import Flask, render_template
from flask_restful import Resource, Api
import requests
import psycopg2
import json

app = Flask(__name__)
api = Api(app)

DB_PASSWORD = "password"
DB_USER = "yggindex"
DB_NAME = "yggindex"
DB_HOST = "localhost"

# count peer alive if it was available not more that amount of seconds ago
# I'm using 1 hour beause of running cron job every 15 minutes
ALIVE_SECONDS = 3600 # 1 hour


def age_calc(ustamp):
    if (time.time() - ustamp) <= ALIVE_SECONDS:
        return True
    else:
        return False

# active nodes
class nodesCurrent(Resource):
    def get(self):
        dbconn = psycopg2.connect(host=DB_HOST,\
                                    database=DB_NAME,\
                                    user=DB_USER,\
                                    password=DB_PASSWORD)
        cur = dbconn.cursor()
        nodes = {}
        cur.execute("select * from yggindex")
        for i in cur.fetchall():
            if age_calc(int(i[2])):
                nodes[i[0]] = [i[1], int(i[2])]

        dbconn.commit()
        cur.close()
        dbconn.close()

        nodelist = {}
        nodelist['yggnodes'] = nodes

        return nodelist


# nodes info
class nodesInfo(Resource):
    def get(self):
        dbconn = psycopg2.connect(host=DB_HOST,\
                                    database=DB_NAME,\
                                    user=DB_USER,\
                                    password=DB_PASSWORD)
        cur = dbconn.cursor()
        nodes = {}
        cur.execute("select * from yggnodeinfo")
        for i in cur.fetchall():
            if age_calc(int(i[2])):
                nodes[i[0]] = json.loads(i[1])

        dbconn.commit()
        cur.close()
        dbconn.close()

        nodeinfo = {}
        nodeinfo['yggnodeinfo'] = nodes

        return nodeinfo


@app.route("/")
def fpage():
    dbconn = psycopg2.connect(host=DB_HOST,\
                                database=DB_NAME,\
                                user=DB_USER,\
                                password=DB_PASSWORD)
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


#sort out the api request here for the url
api.add_resource(nodesCurrent, '/current')
api.add_resource(nodesInfo, '/nodeinfo')

if __name__ == '__main__':
    app.run(host='::', port=3000)
