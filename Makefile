build:
	docker build \
		-t c2dhunilu/miller-v2 \
		--build-arg GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD) \
		--build-arg GIT_REVISION=$(shell git rev-parse --short HEAD) .

run-dev:
	cd docker && docker-compose -f docker-compose.dev.yml up
