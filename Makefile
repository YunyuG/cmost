bag:
	pip3 uninstall cmost -y
	python -m build -w 
	pip3 install ./dist/cmost-0.2-py3-none-any.whl

lint:
	flake8 src/ --count --ignore=W503 --max-line-length=127 --statistics