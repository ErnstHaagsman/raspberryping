#!/usr/bin/env python

# Usage: ping.py [host]
import os
import sys

import psycopg2
import re
import subprocess32

from pingmodel import Ping

if len(sys.argv) != 2:
    print("Usage: ping.py [host]")
    exit(1)

host = sys.argv[1]
user = os.getlogin()

# Do the pings
ping_output = subprocess32.check_output(["ping", host, "-c 5"])
pings = []

for line in ping_output.split('\n'):
    if re.match("\d+ bytes from", line):
        bytes_received = line.split()[0]
        parts = re.search('ttl=(\d+) time=(\d+\.\d+) ms', line.split(':')[1])
        ttl = parts.group(1)
        time = parts.group(2)

        ping = Ping(host, time, ttl, bytes_received)
        pings.append(ping)

# with psycopg2.connect('dbname={} user={}'.format(user, user)) as conn:
#     pass
