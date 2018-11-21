# vserv.py

This server collects dht views from volunteer nodes from all over the network to get a better picture of the network as a whole.  

## Install & Setup

This install assumes your using Linux.  

First install postgres and setup a database & username called yggindex and a password of your choice.  

Once you have done this open vserv.py and edit "DB_PASSWORD" to use the password you set, also change DB_host if your running the Database on another machine:

    DB_PASSWORD = "yourpassword"<edit
    DB_USER = "yggindex"
    DB_NAME = "yggindex"
    DB_HOST = "localhost"

Once you have done this you will need to start vserv.py with the option gentables to create the needed tables:

    python vserv.py gentables

After this stop Vserv.py and start it again with out the option gentables and that should be it running now ready to accept views from other nodes using send-view.py
