import socket
import json
import sys

GETDHT = '{"request":"getDHT", "keepalive":true}'
GETSWITCHPEERS = '{"request":"getSwitchPeers"}'
SERVER = "y.yakamo.org"

#gives the option to get data from an external server instead and send that
#if no options given it will default to localhost instead
if len(sys.argv) == 3:
    host_port = (sys.argv[1], sys.argv[2])
else:
    host_port = ('localhost', 9001)

def send_view_to_server(tosend):
    if tosend:
        attempts = 3
        while attempts:
            try:
                conn = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                conn.connect((SERVER, 45671))
                conn.send(tosend)
                conn.close()
                print "sent ok"
                break
            except:
                attempts -= 1


def collect_dht_getswitchpeers(serport):
    try:
        ygg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ygg.connect(host_port)

        ygg.send(GETDHT)
        dhtdata = json.loads(ygg.recv(1024 * 15))

        ygg.send(GETSWITCHPEERS)
        switchdata = json.loads(ygg.recv(1024 * 15))

        temp_dict = {}
        temp_dict["dhtpack"] = dhtdata
        temp_dict["switchpack"] = switchdata

        return json.dumps(temp_dict).encode()
    except:
        return None

send_view_to_server(collect_dht_getswitchpeers(host_port))
