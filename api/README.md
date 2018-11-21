# niflheim-api.py

This api provides a web interface to see some basic stats on the data vserv.py has collected and also provides and easy way to get the data through the api.  

## Install & Setup

First thing you are going to do is configure niflheim-api.py to use the Postgres databse you setup for vserv.py.  

So open niflheim-api.py:

    DB_PASSWORD = "password"
    DB_USER = "yggindex"
    DB_NAME = "yggindex"
    DB_HOST = "localhost"

Make sure the above matches what you have in vserv.py.  

The API will startup on port 3000 and accept all ipv6 connections if you want to change this edit the last line:  

    app.run(host='::', port=3000)
