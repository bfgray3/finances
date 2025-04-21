FROM python:3.12

WORKDIR /usr/src/uv

ENV PATH=/venv/bin:$PATH UV_NO_CACHE=true

RUN : \
  && pip --no-cache-dir --disable-pip-version-check install uv \
  && uv venv --seed /venv \
  && :
