clean:
	rm -r build dist
	rm -r src/*.egg-info
	rm -r __pycache__

build:
	pip3 uninstall cmost -y
	python -m build -w 

install:
	make build
	pip3 install ./dist/*.whl