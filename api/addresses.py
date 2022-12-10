#!/usr/bin/env python

import json
from pk2addr import keyTo128BitAddress

with open('api/result.json', 'r') as f:
    data = json.load(f)

addlist = open("api/addresses.txt", "w")

for key, _ in data['yggnodes'].items():
    addlist.write(keyTo128BitAddress(key) + "\n")

addlist.close()
