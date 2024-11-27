FROM python:3.7

ARG home=/home/notes

RUN pip install pipenv==2020.6.2

WORKDIR ${home}
USER ${user}

COPY . /${home}
USER root
USER ${user}

RUN pipenv install

EXPOSE 5000

ENV FLASK_APP ${home}/notes/autoapp.py
CMD pipenv run python3 scripts/check_create_database.py && \
	pipenv run flask db upgrade && \
	pipenv run flask run --host=0.0.0.0 --port=5000

