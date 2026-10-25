.PHONY: setup dev test seed reset smoke serve build-web e2e tunnel reader-eval purge-images

setup:
	python tasks.py setup

dev:
	python tasks.py dev

test:
	python tasks.py test

seed:
	python tasks.py seed

reset:
	python tasks.py reset

smoke:
	python tasks.py smoke

serve:
	python tasks.py serve

build-web:
	python tasks.py build-web

e2e:
	python tasks.py e2e

tunnel:
	python tasks.py tunnel

reader-eval:
	python tasks.py reader-eval

purge-images:
	python tasks.py purge-images
