# Miller
a very basic django app to run "digital exhibition websites"

# Install for development
We use docker to make development easier:

    cp docker/.env.example docker/.env

edit the `./docker/.env` file using a proper database name and change the password; then
copy the `./example.env` file to `.env` and fill the fields using the same database name and password.
This second step is needed because the **environment variable names** are different in
docker and in miller.

    SECRET_KEY=*****
    DEBUG=True
    MILLER_DATABASE_NAME=your db name
    MILLER_DATABASE_USER=your db user
    MILLER_DATABASE_PASSWORD=your db pass
    MILLER_DATABASE_HOST=localhost

then start the development docker with:

    make run-dev


This will install all images (redis, postgres...) and build locally celery and miller for you.
`Watchdog` takes care of restarting miller and celery when a py file change in the codebase.

For the first time, of whenever a new migration is available, make sure the db is aligned with:

    make run-migrate

then test that everything works as expected:

    make run-test

To create a new superuser

    docker exec -it docker_miller_1 python manage.py makemigrations

## Add support for the visual editor
The Visual Editor is our favorite way to handle themes and documents in Miller.
It is a React app that connects flawlessy with the Miller JSON based api, and a few Configuration
are needed to make the connection

Create a new *Application* instance in Miller admin. [This](http://localhost/admin/oauth2_provider/application/add/)
will be the URL if you run with the development docker compose. Fill with **Client Type**
set to `Public` and **Authorization Grant Type** to `Resource owner password-based`.

Put the given **Client Id** inside the .env file of the VisualEditor along with
the relative URL of the JSON schema to validate documents:

    REACT_APP_DOCUMENT_SCHEMA=
    REACT_APP_MILLER_CLIENT_ID=


## Install without docker (deprecated)

To install the correct version of python, you can follow
the doc at https://hackernoon.com/reaching-python-development-nirvana-bb5692adf30c

    pyenv installs 3.8.0
    pyenv local 3.8.0

In order to install pipenv using the correct version of python,
use the `pip` module that is shipped with local python version:

    python -m pip install pipenv

Install the library `imagemagick6` according to your OS, then install requirements:

    pipenv install


## Run using pipenv
Copy the `./env.example` file to `./.development.env`, then edit the values accoring to your system.

An example of a `./.development.env` file:

    SECRET_KEY=*****
    DEBUG=True
    MILLER_DATABASE_NAME=your db name
    MILLER_DATABASE_USER=your db user
    MILLER_DATABASE_PASSWORD=your db pass
    MILLER_DATABASE_HOST=localhost

These values replace the default values in `./miller/settings.py` thanks to
the method `get_env_variable`:

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

All values in `get_env_variable` can be replaced with the one of your choice
(e.g; postgres or redis port number can be changed)

Complete the intallation:

    ENV=development pipenv run ./manage.py migrate

Run with:

    ENV=development pipenv run ./manage.py runserver

In parallel, launch the celery tasks manager:

    ENV=development pipenv run celery -A miller worker -l info

## test
Use test runner without DB:

    ENV=development pipenv run ./manage.py test --testrunner=miller.test.NoDbTestRunner
