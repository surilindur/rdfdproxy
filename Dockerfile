FROM python:alpine

ADD rdfdproxy /opt/rdfdproxy

ADD requirements.txt /opt/rdfdproxy/requirements.txt

WORKDIR /opt/rdfdproxy

RUN python -m pip install --upgrade pip setuptools
RUN python -m pip install -r requirements.txt
RUN python -m pip install gunicorn>=23.0.0

RUN adduser --no-create-home --disabled-password --uid 1000 --shell /bin/sh rdfdproxy

USER rdfdproxy

ENTRYPOINT [ "gunicorn", "app:app" ]
