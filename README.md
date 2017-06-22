Raspberry Ping
==============

A smokeping style internet connection quality monitoring tool.

Usage
-----

Set up postgres for peer authentication: create a postgres role
with the same name as the linux account you want to run the 
scripts on. Then create a database with the same name.

Add ping.py [hostname] to the crontab of that user:

    ping.py jetbrains.com

Run the Flask app in analyze.py to get a web interface to
see the results

    python analyze.py

For additional details, read the blog post linked from the
repository.