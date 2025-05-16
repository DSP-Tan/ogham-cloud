.PHONY: setup_venv

setup_venv:
	pyenv install -s 3.13.1
	pyenv virtualenv 3.13.1 ogham
