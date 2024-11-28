======
Notes
======

Notes is a user sign in and notes management project, I based my project
in a MVC architeture and is the one I used for production, that I created 
using flask framework and a postgres database. The main reason of my 
choosing for this framwork is due to the amount of support it has in
labraries and other tools that can help with deployment. The database
was something a little new to me I have more experience with mysql but
still I felt it was a good opportunities to learn more, also postgres has
many commom thing and improvements compared to mysql. Lastly, to debug all
my code I used postmand which is really beneficial to keep all my API calls
and reuse them, Render to host my database and deployment and Visual Studio
for error checking. 

Requirements
------------

To start working on notes, you will need the following software:

- Python ≥ 3.6
- pip
- pipenv ≥ 9.0
- GNU Make

Some extra depencies can be used to ease development and testing, but
these are optional:

- PostgresSQL or other SQL

These can be installed as follows:

Arch Linux
^^^^^^^^^^

.. code-block:: sh

    sudo pacman -S make python python-pip
    sudo pip3 install pipenv
    # Optional dependencies
    sudo pacman -S sqlite

macOS
^^^^^

.. code-block:: sh

    brew install make --with-default-names
    brew install python3
    pip3 install pipenv
    # Optional dependencies
    brew install sqlite

Ubuntu (≥ 16.10)
^^^^^^^^^^^^^^^^

.. code-block:: sh

    sudo apt-get install make python3.6 python3-pip
    sudo pip3 install pipenv
    # Optional dependencies
    sudo apt-get install sqlite3

Getting Started
---------------

Once the dependencies are installed on your system, you should be able
to run the following from the root of the repository and see all tests
succeed:

.. code-block:: sh

    pipenv run pytest --cov=notes tests/unit
    pipenv run pytest --cov=notes tests/integration


This command will also take care of installing any required python
packages, as well as setting up a virtual environment for you, to
avoid conflicts with python packages used by other projects.


Environment Set-up
^^^^^^^^^^^^^^^^^^

Notes reads environment specific configuration through environment variables.
To avoid having to constantly `export` such variables in your shell when developing,
a set of environment definition files are provided under `envs/`. To use
one of them, use the `.` or `source` command of your shell.

For instance, if you intend to develop against a local PostgresSQL database
in a docker container (see PostgresSQL section below for details), you would
run the following:

.. code-block:: sh

   .envs/local-psql

Refer to the next section for details on each of those options.

Database Set-up
^^^^^^^^^^^^^^^

PostgresSQL
~~~~~

If instead you want Notes to connect to a PostgresSQL database, you first
need to have access to a running PostgresSQL instance. The easiest way to do
so is to use the provided utility script which will spawn a PostgresSQL
instance using Docker for you:

.. code-block:: sh

    source ./envs/local-psql
    docker-compose up postgresql -d --build

To add the new database run the following command:

.. code-block:: sh

    pipenv run python  scripts/check_create_database.py

At this point, the database will be devoid of any tables. To populate
it, we use schema migration scripts, which you can run like so:

.. code-block:: sh

    pipenv run flask db upgrade


Running Notes
^^^^^^^^^^^^^^

To run Notes using Flask's built-in development server, you can run
the following:

.. code-block:: sh

    pipenv run flask run

Generate SQLAlchemy Migration Scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Whenever you make changes to the models in `notes.domain.models` you will need
to run the following command:

.. code-block:: sh

    pipenv run flask db migrate

Note that it the migration scripts are not currently compatible with SQLite, so
you will need to run this after setting up a PostgresSQL database as mentioned in the
earlier PostgresSQL specific section on database setup.

In addition to automatically generating migration scripts in this way it may
also be necessary for you to tweak the generated scripts to accomodate
backwards-compatibility for old database entries.

Learning Material and References
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SQLAlchemy
~~~~~~~~~~

- `SQLAlchemy Docs`_
- `ORM tutorial`_
- `ORM recipes`_
- `More ORM recipes`_

Alembic
~~~~~~~

- `Alembic Tutorial`_
- `Alembic Docs`_
- `Flask Migrate Docs`_

.. _SQLAlchemy docs: https://docs.sqlalchemy.org/en/latest/
.. _ORM tutorial: https://docs.sqlalchemy.org/en/latest/orm/tutorial.html
.. _ORM recipes: https://docs.sqlalchemy.org/en/latest/orm/examples.html
.. _More ORM recipes: https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes
.. _Alembic Tutorial: http://alembic.zzzcomputing.com/en/latest/tutorial.html
.. _Alembic Docs: http://alembic.zzzcomputing.com/en/latest/index.html
.. _Flask Migrate Docs: https://flask-migrate.readthedocs.io/en/latest/
