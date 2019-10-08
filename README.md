# niflheim-api.py

Niflheim-api provides both a web interface and an api. The web interface is used to see some basic stats on the data vserv.py has collected and the API provides raw data in JSON format.  

## Install & Setup


Install the following python packages either via your package manager or Pip: 

    flask  
    flask_restful  
    psycopg2  


Configure niflheim-api.py to use the Postgres databse you setup for vserv.py.  

__So open niflheim-api.py:__  

    DB_PASSWORD = "password"
    DB_USER = "yggindex"
    DB_NAME = "yggindex"
    DB_HOST = "localhost"

Make sure the above matches what you have in the crawler.  

The API will startup on port 3000 and accept all ipv6 connections if you want to change this edit the last line:  

    app.run(host='::', port=3000)

__Accessing the API data:__  

    http://exmaple.com:3000/current  

Add yggapi.services to systemd.  
