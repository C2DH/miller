BUILD_TAG ?= latest
ENV ?= development

build:
	docker build \
		--no-cache \
		--progress=plain \
		-t c2dhunilu/miller-v2:${BUILD_TAG} \
		--build-arg GIT_TAG=$(shell git describe --tags) \
		--build-arg GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD) \
		--build-arg GIT_REVISION=$(shell git rev-parse --short HEAD) . &> build.log

run-latest:
	cd docker && docker-compose -f docker-compose.yml up --build

run-down:
	cd docker && docker-compose down --remove-orphans

run-dev:
	export GIT_TAG=$(shell git describe --tags)\
	&& export GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD) \
	&& export GIT_REVISION=$(shell git rev-parse --short HEAD) \
	&& cd docker && docker-compose -f docker-compose.dev.yml up --force-recreate

run-pipenv:
	cd docker && docker compose down --remove-orphans && \
	docker compose --env-file=../.${ENV}.env -f docker-compose.pipenv.yml up

run-dev-build:
	export GIT_TAG=$(shell git describe --tags)\
	&& export GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD) \
	&& export GIT_REVISION=$(shell git rev-parse --short HEAD) \
	&& cd docker && docker-compose -f docker-compose.dev.yml up --force-recreate --build

run-dev-detach:
	export GIT_TAG=$(shell git describe --tags)\
	&& export GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD) \
	&& export GIT_REVISION=$(shell git rev-parse --short HEAD) \
	&& cd docker && docker-compose -f docker-compose.dev.yml up --build -d

run-test:
	docker exec -it docker_miller_1 python manage.py test --testrunner=miller.test.NoDbTestRunner

run-migrate:
	docker exec -it docker_miller_1 python manage.py migrate

run-make-migrations:
	docker exec -it docker_miller_1 python manage.py makemigrations

run-test-celery:
	docker exec -it docker_miller_1 python manage.py celery_test

run-import-from-google:
	docker exec -it docker_miller_1 python manage.py document_import_from_google_spreadsheet \
	&& docker exec -it docker_miller_1 \
    python manage.py document_import_from_json /contents/document_import_from_gs_${GOOGLE_SPREADHSEEET_ID}.json
