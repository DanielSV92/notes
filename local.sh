#!/bin/bash

source `dirname $0`/.venv/bin/activate

export FLASK_APP=`dirname $0`/notes/autoapp.py
. envs/dev-local

pipenv run flask db upgrade
pipenv run flask run --host=0.0.0.0 --port=5000
