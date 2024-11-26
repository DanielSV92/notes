PIPENV_INSTALL_ENV =
PIPENV_INSTALL_FLAGS = --dev --ignore-pipfile

.PHONY: all clean init lint test del-extra

all: init lint test del-extra

clean:
	git clean -fdX

init:
	$(PIPENV_INSTALL_ENV) pipenv install

lint: init
	pipenv run isort --apply --recursive notes tests
	pipenv run yapf --in-place --recursive notes tests

test-unit: init
	export TMPDIR=${PWD} # for macs
	pipenv run pytest --cov=notes tests/unit

test-integration: init
	pipenv run pytest --cov=notes tests/integration $(test)

test: test-unit

del-extra:
	-rm -rf ./*.egg-info
	-rm -rf build
	-rm -rf dist
	-rm -rf htmlcov
	-rm -rf .pytest_cache
	-rm .coverage
