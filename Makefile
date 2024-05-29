.PHONY: build-uv

build-uv: pyproject.toml Dockerfile
	docker build . -t pip-uv

requirements.txt: build-uv
	# redirect here instead of using `-o requirements.txt` to simplify the permissions on this file
	docker run --rm -v $(shell pwd):/usr/src/uv pip-uv uv pip compile pyproject.toml > requirements.txt
