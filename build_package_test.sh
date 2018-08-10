#
# Script to build & upload the package
#
# The Python Quants GmbH
#
rm dist/*

python setup.py sdist bdist_wheel

twine upload --repository-url https://test.pypi.org/legacy/ dist/*
