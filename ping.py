#!/usr/bin/python

# Usage: ping.py [host]
import os
import sys

from datetime import datetime
import psycopg2
import re

import pwd
import subprocess32

from pingmodel import Ping

if len(sys.argv) != 2:
    print("Usage: ping.py [host]")
    exit(1)

host = sys.argv[1]

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
