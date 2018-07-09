from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify
import time
import sys
import os

#check if a database exists or not
db_path = "vservdb/yggindex.db"
if not os.path.exists(db_path):
    print "could not find a database"
    sys.exit(0)

db_connect = create_engine('sqlite:///' + db_path)
app = Flask(__name__)
api = Api(app)

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

#nodes that may not be active anymore or have been offline for a while such as laptops
#could be used as last seen
class nodes_old(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from yggindex")
        nodes = {}
        for i in query.cursor.fetchall():
            if not age_calc(i[2]):
                nodes[i[0]] = [i[1],i[2]]
        nodelist = {}
        nodelist['yggnodes'] = nodes
        return nodelist

#return entire database of nodes regardless of age
class nodes_all(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from yggindex")
        nodes = {}
        for i in query.cursor.fetchall():
            nodes[i[0]] = [i[1],i[2]]
        nodelist = {}
        nodelist['yggnodes'] = nodes
        return nodelist

#sort out the api request here for the url
api.add_resource(nodes_current, '/current')
api.add_resource(nodes_old, '/old')
api.add_resource(nodes_all, '/all')

if __name__ == '__main__':
     app.run(host='::', port=3000)
