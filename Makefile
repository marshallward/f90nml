.PHONY: test
test:
	python -m unittest discover -v -s tests

.PHONY: test.pypa
test.pypa:
	rm -rf dist build f90nml.egg-info
	python -m build
	twine check dist/*
