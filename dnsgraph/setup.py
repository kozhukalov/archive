from setuptools import setup

setup(
    name='dnsgraph',
    version='0.1',
    packages=['dnsgraph'],
    entry_points = {
        'console_scripts': [
            'dnsgraph=dnsgraph.cmd:main',
            'dnsgraph-gen=dnsgraph.tests.gen:main'
        ],
    }
)
