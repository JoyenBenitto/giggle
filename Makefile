.PHONY: build serve clean install

build:
	giggle build

serve:
	giggle serve

clean:
	rm -rf dist/

install:
	pip install -e .
