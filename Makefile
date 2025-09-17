.PHONY: setup_venv

include .env
export $(shell sed -n 's/^\([^#]*\)=.*/\1/p' .env)

setup_venv:
	pyenv install -s 3.13.1
	pyenv virtualenv 3.13.1 ogham

sync_to_gcs:
	gsutil rsync -r Exams gs://$(BUCKET_NAME)
