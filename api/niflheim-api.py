from flask import Flask, request, render_template
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify
import time
import sys
import os
import time
import requests
import psycopg2

app = Flask(__name__)
api = Api(app)

DB_PASSWORD = "password"
DB_USER = "yggindex"
DB_NAME = "yggindex"
DB_HOST = "localhost"

def get_nodelist():
    data = requests.get("use the raw view of the github nodelist", timeout=1)
    nodes = [x.split() for x in data.text.split('\n') if x]
    
    index_table = {}

    for x in nodes:
        index_table[x[0]] = x[1]
    return index_table


def check_nodelist(nodetable, key):
    if nodetable:
        if nodetable.get(key):
            return nodetable.get(key)
        else:
            return key
    else:
        return key


def age_calc(ustamp):
    if (time.time() - ustamp) <= 14400 :
        return True
    else:
        return False

#active nodes in the past 4hrs
class nodes_current(Resource):
    def get(self):
        dbconn = psycopg2.connect(host=DB_HOST,database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = dbconn.cursor()
        nodes = {}
        cur.execute("select * from yggindex")
        for i in cur.fetchall():
            if age_calc(int(i[2])):
                nodes[i[0]] = [i[1],int(i[2])]

        dbconn.commit()
        cur.close()
        dbconn.close()

        nodelist = {}
        nodelist['yggnodes'] = nodes

        return nodelist


@app.route("/")
def fpage():
    dbconn = psycopg2.connect(host=DB_HOST,database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cur = dbconn.cursor()
    nodes = {}
    cur.execute("select * from yggindex")

    for i in cur.fetchall():
        if age_calc(int(i[2])):
            nodes[i[0]] = [i[1],int(i[2])]

    dbconn.commit()
    cur.close()
    dbconn.close()

    return render_template('index.html', nodes = str(len(nodes)))


@app.route("/contrib")
def cpage():
    try:
        NODELIST = get_nodelist()
        print "list exists"
    except:
        print "failed"
        NODELIST = None

    dbconn = psycopg2.connect(host=DB_HOST,database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cur = dbconn.cursor()
    cur.execute("select * from contrib")
    nodes = []

    for i in cur.fetchall():
        if age_calc(int(i[1])):
            nodes.append(i[0])

    dbconn.commit()
    cur.close()
    dbconn.close()

    dnodes = []
    for x in nodes:
        dnodes.append(check_nodelist(NODELIST, x))

    dnodes.sort(reverse=True)

    return render_template('contrib.html', contribnodes = dnodes, nocontribs=str(len(dnodes)))


#sort out the api request here for the url
api.add_resource(nodes_current, '/current')

if __name__ == '__main__':
     app.run(host='::', port=3000)
