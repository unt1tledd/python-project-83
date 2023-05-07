dev:
	poetry run flask --app page_analyzer:app --debug run

all: start db-reset schema-load

schema-load:
	psql python-project-83 < database.sql

db-create:
	`createdb python-project-83`

db-reset:
	dropdb python-project-83 || true
	createdb python-project-83

connect:
	psql -d python-project-83

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

install:
	poetry install

build:
	poetry build
