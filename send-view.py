import socket
import json

GETDHT = '{"request":"getDHT", "keepalive":true}'
GETSWITCHPEERS = '{"request":"getSwitchPeers"}'
SERVER = "y.yakamo.org"


def send_view_to_server(tosend):
    if tosend:
        attempts = 3
        while attempts:
            try:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.sendto(tosend, (SERVER, 45671))
                break
            except:
                attempts -= 1


def collect_dht_getswitchpeers():
    try:
        ygg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ygg.connect(('localhost', 9001))

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

send_view_to_server(collect_dht_getswitchpeers())
