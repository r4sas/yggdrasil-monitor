#some of this code was contributed by Arcelier
#original code https://github.com/Arceliar/yggdrasil-map/blob/master/scripts/crawl-dht.py

import psycopg2
import json
import socket
import sys
import time
import ipaddress

visited = dict() # Add nodes after a successful lookup response
rumored = dict() # Add rumors about nodes to ping
timedout = dict()

host_port = ('localhost', 9001)

DB_PASSWORD = "password"
DB_USER = "yggindex"
DB_NAME = "yggindex"
DB_HOST = "localhost"

def recv_until_done(soc):
    all_data = []
    while True:
        incoming_data = soc.recv(8192)
        if not incoming_data:
            soc.close()
            break
        all_data.append(incoming_data)
    return ''.join(all_data)


def getDHTPingRequest(key, coords, target=None):
    if target:
        return '{{"request":"dhtPing", "box_pub_key":"{}", "coords":"{}", "target":"{}"}}'.format(key, coords, target)
    else:
        return '{{"request":"dhtPing", "box_pub_key":"{}", "coords":"{}"}}'.format(key, coords)


def doRequest(req):
    try:
        ygg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ygg.connect(host_port)
        ygg.send(req)
        data = json.loads(recv_until_done(ygg))
        return data
    except:
        return None


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
        print "database error inserting"

def handleResponse(address, info, data):
    global visited
    global rumored
    global timedout

    timedout[str(address)] = {'box_pub_key':str(info['box_pub_key']), 'coords':str(info['coords'])}

    if not data:
        return
    if 'response' not in data:
        return
    if 'nodes' not in data['response']:
        return
    for addr,rumor in data['response']['nodes'].iteritems():
        if addr in visited: continue
        rumored[addr] = rumor
    if address not in visited:
        visited[str(address)] = info['coords']
    if address in timedout: 
        del timedout[address]


# Get self info
selfInfo = doRequest('{"request":"getSelf"}')

# Initialize dicts of visited/rumored nodes
for k,v in selfInfo['response']['self'].iteritems():
    rumored[k] = v

# Loop over rumored nodes and ping them, adding to visited if they respond
while len(rumored) > 0:
    for k,v in rumored.iteritems():
        handleResponse(k, v, doRequest(getDHTPingRequest(v['box_pub_key'], v['coords'])))
        break 
    del rumored[k]
#End

for x, y in visited.iteritems():
    if valid_ipv6_check(x) and check_coords(y):
        insert_new_entry(x, y)
