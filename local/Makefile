SHELL:=/bin/bash
.PHONY=init,run

init: 
	python3 -m venv .env &&\
	source .env/bin/activate &&\
	pip3 install -r requirements.txt

run:
	source .env/bin/activate &&\
	python run.py
