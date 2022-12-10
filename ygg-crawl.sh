#!/bin/bash

ulimit -n 4096

YGGCRAWL="/opt/yggdrasil-crawler/crawler"
YGGAPIPATH="/opt/yggdrasil-api"

TMPFILE="api/current.json"
CRAWLFILE="api/result.json"

# Crawler timeout in minutes. It must be lesser then crontab job period
# Increased to 50 minutes and crontab runs hourly due to network instabillity
#CRAWLTIMEOUT=50

##############################################################################

cd $YGGAPIPATH

#let "TIMEOUT = $CRAWLTIMEOUT * 60"
#timeout $TIMEOUT $YGGCRAWL > $TMPFILE 2>logs/crawler.log

$YGGCRAWL > $TMPFILE 2>logs/crawler.log

if [[ $? == 0 ]] # Crawler not triggered error or was killed
then
	# add a little delay...
	sleep 3
	mv -f $TMPFILE $CRAWLFILE
	venv/bin/python api/importer.py > logs/importer.log 2>&1
	venv/bin/python api/addresses.py > logs/addresses.log 2>&1
	venv/bin/python api/updateGraph.py > logs/graph.log 2>&1
fi
