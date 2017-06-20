create table pings
(
	recorded_at timestamp with time zone default now(),
	destination text,
	ttl integer,
	bytes_received integer,
	pingtime numeric
);

create index pings_recorded_at on pings(recorded_at);