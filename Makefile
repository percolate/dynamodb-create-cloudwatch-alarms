develop:
	python setup.py develop

undevelop:
	python setup.py develop --uninstall

test:
	flake8 dynamodb_create_cloudwatch_alarms

clean:
	rm -rf dynamodb_create_cloudwatch_alarms.egg-info/
	rm -rf dist/

release: clean
	python setup.py sdist
	twine upload dist/*