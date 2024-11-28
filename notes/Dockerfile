FROM python:3.7
ARG home=/home/notes
ARG user=notes
ARG group=notes
ARG uid=5571
ARG gid=5571

RUN addgroup --gid ${gid} ${group} \
    &&  adduser --home /home/${user} \
                --shell /bin/bash \
                --uid ${uid} \
                --gid ${gid} \
                --disabled-password ${user}

RUN pip3 install --no-cache-dir --trusted-host pypi.python.org pipenv

WORKDIR ${home}
COPY . /${home}
USER root
USER ${user}
RUN pipenv install

EXPOSE 5000

ENV FLASK_APP=${home}/notes/autoapp.py
CMD pipenv run python3 scripts/check_create_database.py && \
	pipenv run flask db upgrade && \
	pipenv run flask run --host=0.0.0.0 --port=5000

