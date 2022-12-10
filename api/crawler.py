#!/usr/bin/env python

# some of this code was contributed by Arcelier
# original code https://github.com/Arceliar/yggdrasil-map/blob/master/scripts/crawl-dht.py
# multithreaded by neilalexander

import psycopg2
import json
import socket
import time
import ipaddress
import traceback
from threading import Lock, Thread
from queue import Queue
from config import DB_PASS, DB_USER, DB_NAME, DB_HOST, useAdminSock, yggAdminTCP, yggAdminSock, saveDefaultNodeInfo, removableFileds

#####

class Worker(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                pass
            finally:
                self.tasks.task_done()

class ThreadPool:
    def __init__(self, threads):
        self.tasks = Queue(128)
        for _ in range(threads):
            Worker(self.tasks)

    def add(self, func, *args, **kargs):
        self.tasks.put((func, args, kargs))

    def wait(self):
        self.tasks.join()

visited = dict() # Add nodes after a successful lookup response
rumored = dict() # Add rumors about nodes to ping
timedout = dict()
nodeinfo = dict()
nodeinfomutex = Lock()
nodeinfopool = ThreadPool(30)

def recv_until_done(soc):
    all_data = []
    while True:
        incoming_data = soc.recv(8192)
        if not incoming_data:
            soc.close()
            break
        all_data.append(incoming_data)
    return b''.join(all_data)


def getDHTPingRequest(key, coords, target=None):
    if target:
        return '{{"request":"dhtPing", "box_pub_key":"{}", "coords":"{}", "target":"{}"}}'.format(key, coords, target).encode('utf-8')
    else:
        return '{{"request":"dhtPing", "box_pub_key":"{}", "coords":"{}"}}'.format(key, coords).encode('utf-8')


def getNodeInfoRequest(key, coords):
    return '{{"request":"getNodeInfo", "box_pub_key":"{}", "coords":"{}"}}'.format(key, coords).encode('utf-8')


def getNodeInfoTask(address, info):
    handleNodeInfo(address, doRequest(getNodeInfoRequest(info['box_pub_key'], info['coords'])))


def doRequest(req):
    try:
        if useAdminSock:
            ygg = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            ygg.connect(yggAdminSock)
        else:
            ygg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ygg.connect(yggAdminTCP)

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
        nodename = ""
        nodejson = "{}"
        if ipv6 in nodeinfo:
            with nodeinfomutex:

                if not saveDefaultNodeInfo:
                    # remove default Node info fields
                    for field in removableFileds:
                        tmprm = nodeinfo[ipv6].pop(field, None)

                nodejson = json.dumps(nodeinfo[ipv6])
                nodename = nodeinfo[ipv6]["name"] if "name" in nodeinfo[ipv6] else ""

        dbconn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = dbconn.cursor()
        timestamp = str(int(time.time()))

        cur.execute(
            "INSERT INTO yggindex (ipv6, coords, unixtstamp, name) VALUES(%s, %s, %s, %s) ON CONFLICT (ipv6) DO UPDATE SET unixtstamp=%s, coords=%s, name=%s;",
            (ipv6, coords, timestamp, nodename, timestamp, coords, nodename)
        )
        cur.execute(
            "INSERT INTO yggnodeinfo (ipv6, nodeinfo, timestamp) VALUES(%s, %s, %s) ON CONFLICT (ipv6) DO UPDATE SET nodeinfo=%s, timestamp=%s;",
            (ipv6, nodejson, timestamp, nodejson, timestamp)
        )

        dbconn.commit()
        cur.close()
        dbconn.close()
    except Exception as e:
        print("database error inserting")
        traceback.print_exc()

def handleNodeInfo(address, data):
    global nodeinfo

    with nodeinfomutex:
        nodeinfo[str(address)] = {}
        if not data:
            return
        if 'response' not in data:
            return
        if 'nodeinfo' not in data['response']:
            return
        nodeinfo[str(address)] = data['response']['nodeinfo']

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
    for addr,rumor in data['response']['nodes'].items():
        if addr in visited: continue
        rumored[addr] = rumor
    if address not in visited:
        visited[str(address)] = info['coords']
    if address in timedout:
        del timedout[address]

    nodeinfopool.add(getNodeInfoTask, address, info)

# Get self info
selfInfo = doRequest('{"request":"getSelf"}'.encode('utf-8'))

# Initialize dicts of visited/rumored nodes
for k,v in selfInfo['response']['self'].items():
    rumored[k] = v

# Loop over rumored nodes and ping them, adding to visited if they respond
while len(rumored) > 0:
    for k,v in rumored.items():
        # print("Processing", v['coords'])
        handleResponse(k, v, doRequest(getDHTPingRequest(v['box_pub_key'], v['coords'])))
        break
    del rumored[k]
# End

nodeinfopool.wait()

for x, y in visited.items():
    if valid_ipv6_check(x) and check_coords(y):
        insert_new_entry(x, y)
