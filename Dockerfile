FROM python:3.7

RUN pip install pipenv

WORKDIR /notes

COPY . /notes
USER root

RUN pipenv install

EXPOSE 5000

ENV FLASK_APP=/notes/notes/autoapp.py
CMD pipenv run python3 scripts/check_create_database.py && \
	pipenv run flask db upgrade && \
	pipenv run flask run --host=0.0.0.0 --port=5000

