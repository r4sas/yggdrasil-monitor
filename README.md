# ygg-node-db
server to collect DHT views from yggdrasil nodes and store in a data base


### send-view.py

Very simple to use just add in crontab and run once an hour.  

__Access External Admin API:__  
If you want to get access to an external Admin API on another server:  

__example__  
send-view.py 192.168.1.100 9001  


## Todo

maybe some kind of testing for current uploads?  
maybe add api token to prevent abuse?  
create restrictions on how much data can be sent maybe?  
add rate limiting for sends and requests/ rate limit in nginx for requests  
add postgress function for alternative use  
