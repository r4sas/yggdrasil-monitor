#add current node count to timeseries table
#can later be used to plot a graph showing daily max nodes on the network
#run every hour

import sqlite3
from sqlite3 import Error
import time

DB_PATH = "vservdb/"


def age_calc(ustamp):
    if (time.time() - ustamp) <= 14400 :
        return True
    else:
        return False


def get_nodes_for_count(db_path):
	conn = sqlite3.connect(db_path + 'yggindex.db')
	query = conn.execute("select * from yggindex")
	nodes = []
	for i in query.fetchall():
	    if age_calc(i[2]):
	        nodes.append(i[1])
	return str(len(nodes))


def add_to_timeseries(db_path):
	# try:
	conn = sqlite3.connect(db_path + "yggindex.db")
	c = conn.cursor()
	c.execute('''INSERT INTO timeseries(max) VALUES(''' + "'"\
				+ get_nodes_for_count(db_path) + "'" + ''')''')
	conn.commit()
	conn.close()


add_to_timeseries(DB_PATH)
