#!/usr/bin/python

import re
import sys
from datetime import datetime

import psycopg2
import subprocess32

# Usage: ping.py [host]
if len(sys.argv) != 2:
    print("Usage: ping.py [host]")
    exit(1)

host = sys.argv[1]


class Ping:
    def __init__(self, destination, ping_time, ttl, bytes):
        self.destination = destination
        self.ping_time = ping_time
        self.ttl = ttl
        self.bytes = bytes

    def __repr__(self):
        return 'PING: {} bytes to {} in {} ms, ttl: {}' \
            .format(self.bytes, self.destination, self.ping_time, self.ttl)


# Do the pings
ping_output = subprocess32.check_output(["ping", host, "-c 5"])
pings = []

for line in ping_output.split('\n'):
    if re.match("\d+ bytes from", line):
        bytes_received = line.split()[0]
        parts = re.search('ttl=(\d+) time=(\d+\.?\d*) ms', line.split(':')[1])

        if not parts:
            print('Could not read: {}'.format(line))

        ttl = parts.group(1)
        time = parts.group(2)

        ping = Ping(host, time, ttl, bytes_received)
        pings.append(ping)

# The raspberry pi has been set up to allow peer authentication locally, and we've created a database
# and a role with the same name as the linux user we're running this script as. Therefore we can use an
# empty connection string.
# See for details: http://initd.org/psycopg/docs/module.html#psycopg2.connect
with psycopg2.connect('') as conn:
    # There is no need for transactions here, no risk of inconsistency etc
    conn.autocommit = True

    cursor = conn.cursor()

    sql_command = """
        INSERT INTO 
          pings
          (destination, bytes_received, ttl, pingtime)
        VALUES
          (%s, %s, %s, %s);
    """

    for ping in pings:
        cursor.execute(sql_command, (ping.destination, ping.bytes, ping.ttl, ping.ping_time))

    print('[{}]: Recorded {} pings'.format(datetime.now(), len(pings)))

    cursor.close()
