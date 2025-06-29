install:
	pip3 uninstall cmost -y
	python -m build -w 
	pip3 install ./dist/*.whl
clean:
	rm -rf build dist
	rm -rf src/*.egg-info
	rm -rf */__pycache__
	rm -rf tests/cache
	rm -rf src/cmost/__pycache__