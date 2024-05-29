.PHONY: build-uv

build-uv: pyproject.toml Dockerfile
	docker build . -t pip-uv

requirements.txt: build-uv
	# TODO: fix permissions for requirements.txt
	docker run --rm -v $(shell pwd):/usr/src/uv pip-uv uv pip compile pyproject.toml -o requirements.txt
