# Niflheim-api

### A collection of tools to support the Niflheim-api:
vserv.py - collects dht views from volunteer nodes.  
niflheim-api.py - presents the data via an API and Web UI  

For installation instructions, you will find them in the README.md in the api folder and the vserv folder.  

### send-view.py

Very simple to use just add in crontab and run once an hour.  

__Access External Admin API:__  
If you want to get access to an external Admin API on another server:  

    send-view.py 192.168.1.100 9001  
