FROM python:3.8.0-alpine
WORKDIR /miller

ARG GIT_TAG
ARG GIT_BRANCH
ARG GIT_REVISION

RUN pip install --upgrade pip

RUN apk add --no-cache \
    postgresql-libs
RUN apk add imagemagick6-dev -U --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev \
    libxslt-dev

COPY miller ./miller
COPY manage.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apk del --no-cache .build-deps
RUN mkdir -p logs

ENV MILLER_GIT_TAG=${GIT_TAG}
ENV MILLER_GIT_BRANCH=${GIT_BRANCH}
ENV MILLER_GIT_REVISION=${GIT_REVISION}
ENV MAGICK_HOME /usr

ENTRYPOINT python ./manage.py runserver
