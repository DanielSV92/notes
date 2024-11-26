#!/bin/bash

source `dirname $0`/.venv/bin/activate

export FLASK_APP=`dirname $0`/smarty/autoapp.py
. envs/dev-local

pipenv run flask db upgrade
pipenv run celery multi start smarty_worker -D -A smarty.autoapp.celery -l debug -E && \
    pipenv run flask run --host=0.0.0.0 --port=5000
