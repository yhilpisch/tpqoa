#
# Setup file for
# tpqoa -- Algorithmic Trading with Oanda
#
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(name='tpqoa',
      version='0.0.55',
      description='tpqoa Algorithmic Trading with Oanda',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Yves Hilpisch',
      author_email='team@tpq.io',
      url='http://home.tpq.io',
      packages=['tpqoa'],
      install_requires=[
          'v20==3.0.25.0',
          'pyyaml'
      ]
      )
