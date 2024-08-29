.PHONY: clean-pycache clean-history clean-all lint format imports pretty

clean-pycache:
	find ./ -type d -name '__pycache__' -exec rm -rf {} +

clean-history:
	-rm history/*.json

clean-all:
	$(MAKE) clean-pycache
	$(MAKE) clean-history

lint:
	poetry run ruff check src/* --fix
	poetry run ruff check app.py --fix

format:
	poetry run ruff format src/*
	poetry run ruff format app.py

imports:
	poetry run ruff check src/* --select I --fix
	poetry run ruff check app.py --select I --fix

pretty:
	$(MAKE) lint
	$(MAKE) format
	$(MAKE) imports
