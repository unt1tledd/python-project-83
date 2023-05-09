DROP TABLE IF EXISTS url_checks;
DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
	id			bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	name		varchar(255) UNIQUE NOT NULL,
	created_at	timestamp
);

CREATE TABLE url_checks (
	id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	url_id bigint REFERENCES urls(id),
	status_code integer,
	h1 varchar(255),
	title varchar,
	description varchar(255),
	created_at timestamp
);