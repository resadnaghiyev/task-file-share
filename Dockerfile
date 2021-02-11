FROM python:3

ENV PYTHONUNBUFFERED=1

WORKDIR usr/src/app

COPY requirements.txt /app/requirements.txt

RUN set -ex \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt


# ADD . .

# CMD gunicorn fileshare.wsgi:application --bind 0.0.0.0:$PORT
