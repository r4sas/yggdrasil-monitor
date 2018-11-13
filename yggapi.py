from flask import Flask, request, render_template
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
#adding rate limiting support
from flask import jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import sys
import os
import time
import requests

#check if a database exists or not
db_path = "vservdb/yggindex.db"
if not os.path.exists(db_path):
    print "could not find a database"
    sys.exit(0)

db_connect = create_engine('sqlite:///' + db_path)
app = Flask(__name__)
api = Api(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["500/day", "60/hour"]
)

def get_nodelist():
    data = requests.get("https://raw.githubusercontent.com/yakamok/yggdrasil-nodelist/master/nodelist")
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


#quickly figure out which is old or new
def age_calc(ustamp):
    if (time.time() - ustamp) <= 14400 :
        return True
    else:
        return False

#active nodes in the past 4hrs
class nodes_current(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from yggindex")
        nodes = {}

        for i in query.cursor.fetchall():
            if age_calc(i[2]):
                nodes[i[0]] = [i[1],i[2]]

        nodelist = {}
        nodelist['yggnodes'] = nodes

        return nodelist


@app.route("/")
def fpage():
    conn = db_connect.connect()
    query = conn.execute("select * from yggindex")
    nodes = {}

    for i in query.cursor.fetchall():
        if age_calc(i[2]):
            nodes[i[0]] = [i[1],i[2]]

    return render_template('index.html', nodes = str(len(nodes)))


@app.route("/contrib")
def cpage():
    try:
        NODELIST = get_nodelist()
        print "list exists"
    except:
        print "failed"
        NODELIST = None

    conn = db_connect.connect()
    query = conn.execute("select * from contrib")
    nodes = []

    for i in query.cursor.fetchall():
        if age_calc(i[1]):
            nodes.append(i[0])

    dnodes = []
    for x in nodes:
        dnodes.append(check_nodelist(NODELIST, x))

    dnodes.sort(reverse=True)

    return render_template('contrib.html', contribnodes = dnodes)


#sort out the api request here for the url
api.add_resource(nodes_current, '/current')
# api.add_resource(nodes_contrib, '/contrib')

if __name__ == '__main__':
     app.run(host='::', port=3000)
