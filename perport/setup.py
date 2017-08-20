from setuptools import setup

setup(
    name="perport",
    version="0.1",
    packages=["perport"],
    entry_points = {
        "console_scripts": [
            "perport=perport.app:main",
        ],
    }
)
