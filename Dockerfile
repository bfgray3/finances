# TODO: need to clean this up

FROM python:3.13

RUN pip install databases[aiomysql] polars
