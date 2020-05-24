FROM python:3.8.0-alpine
WORKDIR /miller

ARG GIT_BRANCH
ARG GIT_REVISION
ENV MAGICK_HOME=/usr
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


RUN pip install --upgrade pip
RUN pip install -U pipenv
COPY miller ./miller
COPY schema ./schema
COPY manage.py .

# COPY requirements.txt .
# RUN pip install -r requirements.txt
# RUN pip install Wand
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile

RUN apk del --no-cache .build-deps
RUN mkdir -p logs


ENV MILLER_GIT_BRANCH=${GIT_BRANCH}
ENV MILLER_GIT_REVISION=${GIT_REVISION}
ENV MAGICK_HOME /usr
ENTRYPOINT python ./manage.py runserver
