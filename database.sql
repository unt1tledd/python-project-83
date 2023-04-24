DROP TABLE IF EXISTS checks;
DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
	id			bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	name		varchar(255) UNIQUE NOT NONE,
	created_at	timestamp
);

CREATE TABLE checks (
	id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	url_id bigint REFERENCES urls(id),
	request_code integer,
	h1 varchar(255),
	title varchar,
	created_at timestamp
);