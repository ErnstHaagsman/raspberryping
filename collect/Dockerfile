FROM ubuntu:latest
MAINTAINER ernst.haagsman@jetbrains.com

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev python3 python3-dev python3-pip iputils-ping

COPY requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

COPY . /app

CMD ["python3", "-u", "/app/ping.py", "jetbrains.com"]