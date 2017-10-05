FROM ubuntu:latest
MAINTAINER ernst.haagsman@jetbrains.com

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev python-dev python-pip

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD gunicorn --bind=0.0.0.0 --access-logfile - --access-logformat "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s %(L)s" analyze:app