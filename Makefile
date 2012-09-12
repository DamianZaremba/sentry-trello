# https://gist.github.com/3697234
publish:
	python setup.py sdist upload

clean:
	rm -rf *.egg-info
	rm -rf dist
	rm -rf build

.PHONY: publish clean
