FROM python:3.8.0-alpine
WORKDIR /miller
COPY Pipfile Pipfile.lock /miller/
RUN pip install pipenv
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
RUN pipenv install --system
RUN apk del --no-cache .build-deps
RUN mkdir -p logs
COPY miller ./miller
COPY manage.py .

ENV MAGICK_HOME /usr
