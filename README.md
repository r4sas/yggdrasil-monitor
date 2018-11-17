# Niflheim-api

### A collection of tools to support the yggapi:
vserv.py - collects dht views from volunteer nodes.  
yggapi.py - presents the data via an API and Web UI  

### send-view.py

Very simple to use just add in crontab and run once an hour.  

__Access External Admin API:__  
If you want to get access to an external Admin API on another server:  

send-view.py 192.168.1.100 9001  


## Todo

Redesign client server negotiation for data  
add instructions for installtion in the readme  
write script to test the server and api by generating fake data  
