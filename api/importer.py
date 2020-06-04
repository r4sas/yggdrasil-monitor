#!/usr/bin/env python

import psycopg2, json, traceback

#####

# Configuration to use TCP connection or unix domain socket for admin connection to yggdrasil
DB_PASS = "password"
DB_USER = "yggindex"
DB_NAME = "yggindex"
DB_HOST = "localhost"

## Save in database node info fields like buildname, buildarch, etc. (True/False)?
saveDefaultNodeInfo = False
removableFileds = ['buildname', 'buildarch', 'buildplatform', 'buildversion', 'board_name', 'kernel', 'model', 'system']

#####

with open('api/results.json', 'r') as f:
    data = json.load(f)

timestamp = data['meta']['generated_at_utc']

# connect to database
dbconn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
cur = dbconn.cursor()

# start importing
for node in data['topology']:
    nodename = ""
    nodeinfo = {}
    ipv6 = data['topology'][node]['ipv6_addr']
    coords = '[%s]' % (' '.join(str(e) for e in data['topology'][node]['coords']))

    if node in data['nodeinfo']:
        nodeinfo = data['nodeinfo'][node]

        if not saveDefaultNodeInfo:
            # remove default Node info fields
            for field in removableFileds:
                tmprm = nodeinfo.pop(field, None)

    if "name" in nodeinfo:
        nodename = nodeinfo['name']
    elif data['topology'][node]['found'] == False:
        nodename = '? %s' % coords
    else:
        nodename = ipv6

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

