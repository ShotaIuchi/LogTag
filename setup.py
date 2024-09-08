from setuptools import setup, find_packages

setup(
    name='logtag',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'tabulate',
        'hjson',
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
