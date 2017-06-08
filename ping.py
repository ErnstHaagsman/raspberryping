#!/usr/bin/env python

# Usage: ping.py [host]
import os
import sys

import psycopg2
import re
import subprocess32

if len(sys.argv) != 2:
    print("Usage: ping.py [host]")
    exit(1)

host = sys.argv[1]
user = os.getlogin()

# Do the pings
pings = subprocess32.check_output(["ping", host, "-c 5"])

for line in pings.split('\n'):
    if re.match("\d+ bytes from", line):
        bytes_received = line.split()[0]
        parts = re.search('ttl=(\d+) time=(\d+\.\d+) ms', line.split(':')[1])
        ttl = parts.group(1)
        time = parts.group(2)

        print('PING: {} bytes in {} ms, ttl: {}'.format(bytes_received, time, ttl))

# with psycopg2.connect('dbname={} user={}'.format(user, user)) as conn:
#     pass
