FROM python:3.7

ARG home=/home/smarty

RUN pip install pipenv==2020.6.2

WORKDIR ${home}
USER ${user}

COPY . /${home}
USER root

RUN ["/bin/bash", "-c","mkdir .ssh", "chmod 777 /home/smarty/.ssh"]
USER ${user}

RUN pipenv install

EXPOSE 5000

ENV FLASK_APP ${home}/smarty/autoapp.py
CMD pipenv run python3 scripts/check_create_database.py && \
	pipenv run flask db upgrade && \
	pipenv run python3 scripts/init_roles_and_permissions.py && \
	pipenv run python3 scripts/init_fingerprint.py && \
	pipenv run python3 scripts/init_env_features.py && \
	pipenv run python3 scripts/init_cerebro_settings.py && \
	pipenv run python3 scripts/init_metrics.py && \
	pipenv run flask run --host=0.0.0.0 --port=5000

