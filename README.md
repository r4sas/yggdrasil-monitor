# ygg-node-db
server to collect DHT views from yggdrasil nodes and store in a data base


### send-view.py

Very simple to use just add in crontab and run once an hour.  

__Access External Admin API:__  
If you want to get access to an external Admin API on another server:  

__example__  
send-view.py 192.168.1.100 9001  


## Todo

add Triggers to database for self cleaning of old entrys  
add rate limiting for sends and requests  
add postgress function for alternative use  
