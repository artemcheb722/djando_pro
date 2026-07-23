DC = docker compose
LOCALE ?= ru

i18n: makemessages compilemessages
.PHONY: build up down shell migrate restart makemigrations build-up bash test makemessages compilemessages i18n

build:
	${DC} build

up:
	${DC} up

down:
	${DC} down

shell:
	${DC} exec web python manage.py shell

migrate:
	${DC} exec web python manage.py migrate

makemigrations:
	${DC} exec web python manage.py makemigrations

makemessages:
	${DC} exec web python manage.py makemessages -l ${LOCALE}

compilemessages:
	${DC} exec web python manage.py compilemessages


createsuperuser:
	${DC} exec web python manage.py createsuperuser

restart:
	${DC} down && ${DC} up -d

build-up:
	${DC} build && ${DC} up

bash:
	docker exec -it web bash
test:
	${DC} exec web pytest -v
