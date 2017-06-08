class Ping:

    def __init__(self, destination, ping_time, ttl, bytes):
        self.destination = destination
        self.ping_time = ping_time
        self.ttl = ttl
        self.bytes = bytes