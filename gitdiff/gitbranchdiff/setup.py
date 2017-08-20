from setuptools import setup

setup(
    name='gitbranchdiff',
    version='0.1',
    packages=['gitbranchdiff'],
    entry_points = {
        'console_scripts': [
            'gitbranchdiff-csv=gitbranchdiff.cmd:csvdiff'
        ],
    }
)
