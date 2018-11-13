#server for collecting DHT info

import json
import time
import sqlite3
from sqlite3 import Error
import os
import socket
#ipaddress needs to be installed its not part of the standard lib
import ipaddress
import thread

SERVER = ""
DB_PATH = "vservdb/"


def check_coords(coords):
    coord_len = coords.replace(' ', '').replace('[', '').replace(']', '')
    digits_found = [x for x in coord_len if x.isdigit()]

    if len(digits_found) == len(coord_len):
        crus = True
    else:
        crus = False
    return crus


def valid_ipv6_check(ipv6add):
    try:
        if ipaddress.IPv6Address(unicode(ipv6add)):
            addr = True
    except:
        addr = False
    return addr


def isdatabase(db_path):
    if not os.path.exists(db_path + "yggindex.db"):
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        try:
            dbconn = sqlite3.connect(db_path + 'yggindex.db')
            c = dbconn.cursor()
            c.execute('''create table yggindex(ipv6 varchar(45) UNIQUE, coords varchar(50),\
                        dt datetime default (strftime('%s','now')))''')
            c.execute('''create table timeseries(max varchar(45),\
                        dt datetime default (strftime('%s','now')))''')
            c.execute('''create table contrib(ipv6 varchar(45) UNIQUE,\
                        ut unixtime default (strftime('%s','now')))''')
            dbconn.commit()
        except Error as e:
            print(e)
        finally:
            dbconn.close()
    else:
        print("found database will not create a new one")


def insert_new_entry(db_path, ipv6, coords):
    try:
        dbconn = sqlite3.connect(db_path + "yggindex.db")
        dbconn.execute('''INSERT OR REPLACE INTO yggindex(ipv6, coords) VALUES(?, ?)''',\
                    (ipv6, coords)) 
        dbconn.commit()
        dbconn.close()
    except Error as e:
        print e

def contrib_entry(db_path, ipv6):
    try:
        dbconn = sqlite3.connect(db_path + "yggindex.db")
        dbconn.execute('''INSERT OR REPLACE INTO contrib(ipv6) VALUES(''' + "'"\
                        + ipv6 + "'" + ''')''')
        dbconn.commit()
        dbconn.close()
    except Error as e:
        print e

def error_check_insert_into_db(dht, switchpeers, ipv6):
    try:
        if dht.get("status") == "success":
            for x, y in dht["response"]["dht"].iteritems():
                if valid_ipv6_check(x) and check_coords(y["coords"]):
                    insert_new_entry(DB_PATH, x, y["coords"])

        if dht.get("status") == "success":
            for x in switchpeers["response"]["switchpeers"].iteritems():
                if valid_ipv6_check(x[1]["ip"]) and check_coords(x[1]["coords"]):
                    insert_new_entry(DB_PATH, x[1]["ip"], x[1]["coords"])

        contrib_entry(DB_PATH, ipv6)
    except:
        print"error in json file, aborting"


def proccess_incoming_data(datty, ipv6):
    print str(time.time()) + " " + str(ipv6)
    try:
    	ddata = datty.recv(1024 * 20)
	data = json.loads(ddata.decode())
	error_check_insert_into_db(data["dhtpack"], data["switchpack"], ipv6)
    except:
        print "ignoring, data was not json"


isdatabase(DB_PATH)

conn = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
conn.bind((SERVER, 45671))
conn.listen(30)

while True:
    try:
        dataraw, addr = conn.accept()
        thread.start_new_thread(proccess_incoming_data, (dataraw, addr[0]))
    except Exception:
        print "bloop"
