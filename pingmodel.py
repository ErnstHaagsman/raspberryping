class Ping:

    def __init__(self, destination, ping_time, ttl, bytes):
        self.destination = destination
        self.ping_time = ping_time
        self.ttl = ttl
        self.bytes = bytes

    def __repr__(self):
        return 'PING: {} bytes to {} in {} ms, ttl: {}'\
                 .format(self.bytes, self.destination, self.ping_time, self.ttl)