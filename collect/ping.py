#!/usr/bin/python

# Usage: ping.py [host]
import os
import sys

from datetime import datetime

import asyncio
import codecs
import psycopg2
import re

import pwd
import subprocess

class Ping:

    def __init__(self, destination, ping_time, ttl, bytes):
        self.destination = destination
        self.ping_time = ping_time
        self.ttl = ttl
        self.bytes = bytes

    def __repr__(self):
        return 'PING: {} bytes to {} in {} ms, ttl: {}'\
                 .format(self.bytes, self.destination, self.ping_time, self.ttl)

if len(sys.argv) != 2:
    print("Usage: ping.py [host]")
    exit(1)

host = sys.argv[1]

pg_host = os.environ['PGHOST']
pg_user = os.environ['PGUSER']
pg_pass = os.environ['PGPASSWORD']
pg_db = os.environ['PGDATABASE']

async def collect_pings():
    while True:
        # Do the pings
        ping_process = subprocess.run(["ping", host, "-c 5"], stdout=subprocess.PIPE)
        pings = []

        ping_output = codecs.decode(ping_process.stdout, encoding='ascii')

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

        with psycopg2.connect(dbname=pg_db, host=pg_host, user=pg_user, password=pg_pass) as conn:
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

        await asyncio.sleep(30)

print('Pinging {}'.format(host))
loop = asyncio.get_event_loop()
loop.run_until_complete(collect_pings())
