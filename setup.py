import os
import re
from setuptools import setup, find_packages


def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'LogTag', '__init__.py')
    with open(version_file, 'r') as f:
        version_content = f.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


setup(
    name='logtag',
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        'tabulate',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'logtag=LogTag.logtag:main',
        ],
    },
    author='Shota Iuchi',
    author_email='shotaiuchi.develop@gmail.com',
    description='LogTag adds tags to log messages.',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='log, tag',
    url='https://github.com/ShotaIuchi/LogTag',
)
