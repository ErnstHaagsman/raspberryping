FROM ubuntu:latest
MAINTAINER ernst.haagsman@jetbrains.com

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev python-dev python-pip cron iputils-ping

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

ADD run-pings /etc/cron.d/run-pings

RUN chmod 0644 /etc/cron.d/run-pings

COPY . /app

EXPOSE 8000

CMD cron && gunicorn --bind=0.0.0.0 --access-logfile - --access-logformat "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s %(L)s" analyze:app