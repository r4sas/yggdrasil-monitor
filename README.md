# ygg-node-db
server to collect DHT views from yggdrasil nodes and store in a data base


### send-view.py

Very simple to use just add in crontab and run once an hour.  
If you want to get access an external Admin API on another server:

send-view.py ipv4 port  

__example__  
send-view.py 192.168.1.100 9001  


## Todo

add Triggers to database for self cleaning of old entrys  
add postgress function for alternative use  
create an alternative to send-view to collect from multiple nodes and send(rare use case as admin api isnt secure to leave open)  
