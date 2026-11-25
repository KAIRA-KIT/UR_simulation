from setuptools import find_packages
from setuptools import setup

setup(
    name='ur_simulation',
    version='0.0.0',
    packages=find_packages(
        include=('ur_simulation', 'ur_simulation.*')),
)
