#!/usr/bin/env python

import psycopg2, json, traceback
from config import DB_PASS, DB_USER, DB_NAME, DB_HOST, saveDefaultNodeInfo, removableFileds
from pk2addr import keyTo128BitAddress

#####

with open('api/result.json', 'r') as f:
    data = json.load(f)

# connect to database
dbconn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
cur = dbconn.cursor()

# start importing
for key, node in data['yggnodes'].items():
    nodename = ""
    nodeinfo = {}

    if "address" in node:
        ipv6 = keyTo128BitAddress(node['address']) if len(node['address']) == 64 else node['address']
    else:
        ipv6 = keyTo128BitAddress(key)

    if "coords" in node:
        coords = node['coords']
    else:
        continue

    timestamp = node['time']

    if "nodeinfo" in node:
        nodeinfo = node['nodeinfo']

        if not saveDefaultNodeInfo:
            # remove default Node info fields
            for field in removableFileds:
                tmprm = nodeinfo.pop(field, None)

    if "name" in nodeinfo:
        nodename = nodeinfo['name']
    else:
        nodename = '? %s' % coords

    nodeinfo = json.dumps(nodeinfo)

    try:
        cur.execute(
            "INSERT INTO yggindex (ipv6, coords, unixtstamp, name) VALUES(%s, %s, %s, %s) ON CONFLICT (ipv6) DO UPDATE SET unixtstamp=%s, coords=%s, name=%s;",
            (ipv6, coords, timestamp, nodename, timestamp, coords, nodename)
        )
        cur.execute(
            "INSERT INTO yggnodeinfo (ipv6, nodeinfo, timestamp) VALUES(%s, %s, %s) ON CONFLICT (ipv6) DO UPDATE SET nodeinfo=%s, timestamp=%s;",
            (ipv6, nodeinfo, timestamp, nodeinfo, timestamp)
        )

    except Exception as e:
        print("database error inserting")
        traceback.print_exc()

dbconn.commit()
cur.close()
dbconn.close()
