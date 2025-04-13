# TODO: need to clean this up

FROM python:3.13

WORKDIR /usr/src/finances

RUN pip install databases[aiomysql] polars
