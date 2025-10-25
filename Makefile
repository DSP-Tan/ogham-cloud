.PHONY: setup_venv

include .env
export $(shell sed -n 's/^\([^#]*\)=.*/\1/p' .env)

setup_venv:
	pyenv install -s 3.13.1
	pyenv virtualenv 3.13.1 ogham

setup_pdf_scrape_test_resources:
	python -m pdf_scraper.tests.write_tests section  1
	python -m pdf_scraper.tests.write_tests title    1
	python -m pdf_scraper.tests.write_tests subtitle 1
	python -m pdf_scraper.tests.write_cluster_tests

sync_to_gcs:
	gsutil rsync -r Exams gs://$(BUCKET_NAME)

sync_from_gcs:
	gsutil rsync -r gs://$(BUCKET_NAME) Exams

create_english_db:
	psql -U $(POSTGRES_USER) -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'english_exams'" \
		| grep -q 1 \
		&& echo "english_exams exists" \
		|| (echo "creating english_exams" && psql -c "CREATE DATABASE english_exams")
