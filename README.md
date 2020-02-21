# Miller
a very basic django app to run "digital exhibition websites"

# Requirements
Miller works with Postgres databases

# Install with Docker
@todo

# Install for development
We followed the doc at https://hackernoon.com/reaching-python-development-nirvana-bb5692adf30c

    pyenv installs 3.8.0
    pyenv local 3.8.0

In order to install pipenv using the correct version of python,
use pip shipped with local python version:

    python -m pip install pipenv

Then install requirements:

    pipenv install

## configure
Copy the `.example.env` file to `.development.env` and fill the fields:

    SECRET_KEY=*****
    DEBUG=True
    MILLER_DATABASE_NAME=your db name
    MILLER_DATABASE_USER=your db user
    MILLER_DATABASE_PASSWORD=your db pass
    MILLER_DATABASE_HOST=localhost

These values replace the default values in miller/settings.py file thanks to the function `get_env_variable`:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': get_env_variable('MILLER_DATABASE_NAME'),
            'USER': get_env_variable('MILLER_DATABASE_USER'),
            'PASSWORD': get_env_variable('MILLER_DATABASE_PASSWORD'),
            'HOST': get_env_variable('MILLER_DATABASE_HOST', 'localhost'),
            'PORT': get_env_variable('MILLER_DATABASE_PORT', '54320'),
        }
    }

As we're going to use docker for development purposes, remember to copy the postgres credentials to the
`docker/.env` file (use the given `docker/.env.example` file as example):

    POSTGRES_USER=your db name
    POSTGRES_DB=your db user
    POSTGRES_PASSWORD=your db pass

From the folder where the Makefile is, run:

    make run-dev

to initialize or restart the postgres database defined in the docker-compose file.
Finally, run migration and check that the system is working properly:

    ENV=development pipenv run ./manage.py migrate

## run!
Using pipenv:

    ENV=development pipenv run ./manage.py runserver
