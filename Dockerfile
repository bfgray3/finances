FROM python:3.12

WORKDIR /usr/src/uv

ENV PATH=/venv/bin:$PATH PYTHONUNBUFFERED=1

RUN : \
  && pip --no-cache-dir --disable-pip-version-check install uv \
  && uv venv --seed --no-cache /venv \
  && :
