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

Docker compose file used for development is `docker/docker-compose.dev.yml` and as you see expose postgres to the port 54320 and redis to port 63790.
This comes in handy if we want to use those services with external software (eg pgadmin). This allows also to use management commands outside of docker.
For instance, we might run django migration command to check that the system is working properly:

    ENV=development pipenv run ./manage.py migrate

## run!
Using docker for devlopment, from the folder where the Makefile is, run:

    ENV=development make run-dev

Using pipenv:

    ENV=development pipenv run ./manage.py runserver

With celery tasks:

    ENV=development pipenv run celery -A miller worker -l info

## test
Use test runner without DB:

    ENV=development pipenv run ./manage.py test --testrunner=miller.test.NoDbTestRunner
