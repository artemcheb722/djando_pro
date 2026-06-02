DC = docker compose
.PHONY: up down build
build:
	${DC} build
up:
	${DC} up
down:
	${DC} down