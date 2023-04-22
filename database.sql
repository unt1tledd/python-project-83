CREATE TABLE urls (
	id			bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	name		varchar(255) UNIQUE NOT NONE,
	created_at	timestamp
);

CREATE TABLE info (
	id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	request_code integer,
	h1 varchar(255),
	title varchar,
	created_at timestamp
);