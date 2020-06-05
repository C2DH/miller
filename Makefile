build:
	docker build \
		-t c2dhunilu/miller-v2 \
		--build-arg GIT_TAG=$(shell git describe --tags) \
		--build-arg GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD) \
		--build-arg GIT_REVISION=$(shell git rev-parse --short HEAD) .

run-latest:
	cd docker && docker-compose -f docker-compose.yml up --build

run-down:
	cd docker && docker-compose down --remove-orphans

run-dev:
	export GIT_TAG=$(shell git describe --tags)\
	&& export GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD) \
	&& export GIT_REVISION=$(shell git rev-parse --short HEAD) \
	&& cd docker && docker-compose -f docker-compose.dev.yml up --force-recreate

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
