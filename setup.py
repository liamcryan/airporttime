import os
from setuptools import setup, find_packages
from io import open

here = os.path.abspath(os.path.dirname(__file__))

install_requires = ['pytz', 'requests', 'timezonefinder']

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()


setup(name='airporttime',
      version='0.0.0',
      description='convert local time to utc time by airport or vise-versa.',
      long_description=readme,
      author='Liam Cryan',
      author_email='cryan.liam@gmail.com',
      packages=find_packages(),
      install_requires=install_requires,
      include_package_data=True
      )