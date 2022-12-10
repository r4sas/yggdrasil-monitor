#!/usr/bin/env python

# max/min for the day with nodes

import psycopg2
import time
from config import DB_PASS, DB_USER, DB_NAME, DB_HOST, ALIVE_SECONDS

# run every hour

def age_calc(ustamp):
	if (time.time() - ustamp) <= ALIVE_SECONDS :
		return True
	else:
		return False

def get_nodes_for_count():
	dbconn = psycopg2.connect(host=DB_HOST,database=DB_NAME, user=DB_USER, password=DB_PASS)
	cur = dbconn.cursor()
	nodes = {}
	cur.execute("select * from yggindex")

	for i in cur.fetchall():
		if age_calc(int(i[2])):
			nodes[i[0]] = [i[1],int(i[2])]

	cur.close()
	dbconn.close()

	return str(len(nodes))

def add_to_db():
	dbconn = psycopg2.connect(host=DB_HOST,database=DB_NAME, user=DB_USER, password=DB_PASS)
	cur = dbconn.cursor()

	cur.execute('''INSERT INTO timeseries(max, unixtstamp) VALUES(''' + "'" + get_nodes_for_count() + "'," + str(int(time.time())) + ''')''')

	dbconn.commit()
	cur.close()
	dbconn.close()

add_to_db()
