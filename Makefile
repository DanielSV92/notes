PIPENV_INSTALL_ENV =
PIPENV_INSTALL_FLAGS = --dev --ignore-pipfile

.PHONY: all clean init lint test del-extra

all: init lint test del-extra

clean:
	git clean -fdX

init:
	$(PIPENV_INSTALL_ENV) pipenv install

lint: init
	pipenv run isort --apply --recursive smarty tests
	pipenv run yapf --in-place --recursive smarty tests

test-unit: init
	export TMPDIR=${PWD} # for macs
	pipenv run pytest --cov=smarty tests/unit

test-integration: init
	pipenv run pytest --cov=smarty tests/integration $(test)

test: test-unit

del-extra:
	-rm -rf ./*.egg-info
	-rm -rf build
	-rm -rf dist
	-rm -rf htmlcov
	-rm -rf .pytest_cache
	-rm .coverage

# compose-up:
# 	pipenv run python3 scripts/check_create_database.py
# 	pipenv run flask db upgrade
# 	pipenv run python3 scripts/init_roles_and_permissions.py
# 	pipenv run python3 scripts/init_fingerprint.py
# 	pipenv run python3 scripts/init_env_features.py
# 	pipenv run python3 scripts/init_cerebro_settings.py

