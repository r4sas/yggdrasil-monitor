#!/bin/sh

YGGCRAWL="/opt/yggcrawl/yggcrawl" # path to yggcrawl binary
YGGAPIPATH="/opt/yggdrasil-api"   # path to Niflheim-API directory

CRAWLPEER="tcp://127.0.0.1:12345" # Yggdrasil peer address
CRAWLFILE="api/results.json"
CRAWLRETR=3

cd $YGGAPIPATH
$YGGCRAWL -peer $CRAWLPEER -retry $CRAWLRETR -file $CRAWLFILE > api/yggcrawl.log 2>&1
venv/bin/python api/importer.py >> api/yggcrawl.log 2>&1
