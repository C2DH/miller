# Miller
a very basic django app to run "digital exhibition websites"

# Install for development
We use docker to make development easier:
    
    cp docker/.env.example docker/.env

edit the `docker/.env` file setting proper database name and password; then

    make run-dev

Will install all images (redis, postgres...) and build locally celery and miller for you.
`Watchdog` takes care of restarting miller and celery when a py file change in the codebase.

Make sure the db is aligned:

    make run-migrate

then test that everything works as expected:

    make run-test

## Install without docker (not recommended)
We followed the doc at https://hackernoon.com/reaching-python-development-nirvana-bb5692adf30c

    pyenv installs 3.8.0
    pyenv local 3.8.0

In order to install pipenv using the correct version of python,
use pip shipped with local python version:

    python -m pip install pipenv

Install the library imagemagick6, then install requirements:

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

# run!
Using docker for devlopment, from the folder where the Makefile is, run:

    make run-dev

then go to http://localhost:8008

## with pipenv

Using pipenv:

    ENV=development pipenv run ./manage.py runserver

With celery tasks:

    ENV=development pipenv run celery -A miller worker -l info

# test
Use test runner without DB:

    ENV=development pipenv run ./manage.py test --testrunner=miller.test.NoDbTestRunner
