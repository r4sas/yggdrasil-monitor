#server for collecting DHT info

import json
import psycopg2
import time
import os
import socket
import ipaddress
import thread
import sys

SERVER = ""
DB_PASSWORD = "password"
DB_USER = "yggindex"
DB_NAME = "yggindex"
DB_HOST = "localhost"

#To setup tables in the database on first run please use:
#python vserv.py gentables
#This will generate all the tables needed

def create_tables():
    try:
        dbconn = psycopg2.connect(host=DB_HOST,database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = dbconn.cursor()

        cur.execute('''CREATE TABLE yggindex(ipv6 varchar UNIQUE,\
                    coords varchar, unixtstamp varchar)''')
        cur.execute('''CREATE TABLE timeseries(max varchar,\
                    unixtstamp varchar)''')
        cur.execute('''CREATE TABLE contrib(ipv6 varchar UNIQUE,\
                    unixtstamp varchar)''')
        
        dbconn.commit()
        cur.close()
        dbconn.close()
    except:
        print "somethings up, check you created the database correctly"

#check if tables need to be generated or not
if len(sys.argv) > 1:
    if sys.argv[1] == "gentables":
        create_tables()

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


def insert_new_entry(ipv6, coords):
    try:
        dbconn = psycopg2.connect(host=DB_HOST,database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = dbconn.cursor()

        cur.execute('''INSERT INTO yggindex(ipv6, coords, unixtstamp)\
                        VALUES(''' + "'" + ipv6 + "'," + "'" + coords + "'," + str(int(time.time())) + ''')\
                        ON CONFLICT (ipv6) DO UPDATE\
                        SET unixtstamp = ''' + "'" + str(int(time.time())) + "'," +''' \
                        coords = ''' + "'" + coords + "'" + ''';''')

        dbconn.commit()
        cur.close()
        dbconn.close()
    except:
        cur.close()
        dbconn.close()


def contrib_entry(ipv6):
    try:
        dbconn = psycopg2.connect(host=DB_HOST,database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = dbconn.cursor()
        cur.execute('''INSERT INTO contrib(ipv6, unixtstamp)\
                      VALUES(''' + "'" + ipv6 + "'," + str(int(time.time())) + ''')\
                      ON CONFLICT (ipv6) DO UPDATE\
                      SET unixtstamp = ''' + "'" + str(int(time.time())) + "'" + ''';''')
        dbconn.commit()
        cur.close()
        dbconn.close()
    except:
        cur.close()
        dbconn.close()


def error_check_insert_into_db(dht, switchpeers, ipv6):
    try:
        if dht.get("status") == "success":
            for x, y in dht["response"]["dht"].iteritems():
                if valid_ipv6_check(x) and check_coords(y["coords"]):
                    insert_new_entry(x, y["coords"])

        if switchpeers.get("status") == "success":
            for x in switchpeers["response"]["switchpeers"].iteritems():
                if valid_ipv6_check(x[1]["ip"]) and check_coords(x[1]["coords"]):
                    insert_new_entry(x[1]["ip"], x[1]["coords"])

        contrib_entry(ipv6)
    except:
        print"error in json file, aborting"


def proccess_incoming_data(datty, ipv6):
    print str(time.time()) + " " + str(ipv6)
    try:
        ddata = datty.recv(18128)
        data = json.loads(ddata.decode())
        error_check_insert_into_db(data["dhtpack"], data["switchpack"], ipv6)
    except:
        print "ignoring, data was not json"


conn = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
conn.bind((SERVER, 45671))
conn.listen(30)

while True:
    try:
        dataraw, addr = conn.accept()
        thread.start_new_thread(proccess_incoming_data, (dataraw, addr[0]))
    except Exception:
        print "bloop"
