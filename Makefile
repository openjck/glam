.PHONY: build up shell test

build:
	docker-compose build

up:
	docker-compose up

shell:
	docker-compose run --rm server /bin/bash

test:
	docker-compose run --rm server pytest -s --dc=Test glam/
