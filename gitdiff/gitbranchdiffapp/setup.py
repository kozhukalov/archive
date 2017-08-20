from setuptools import setup

setup(
    name='gitbranchdiffapp',
    version='0.1',
    packages=['gitbranchdiffapp'],
    entry_points = {
        'console_scripts': [
            'gitbranchdiffapp=gitbranchdiffapp.app:main',
        ],
    }
)
