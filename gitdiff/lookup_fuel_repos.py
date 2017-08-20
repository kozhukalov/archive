#!/usr/bin/env python

import os
import requests
import json


GIT_ROOT_PATH = os.path.abspath("/home/kozhukalov/utilities/repos")

def lookup_fuel_repos():
    r = requests.get("https://api.github.com/search/repositories?q=fuel-+user:openstack&per_page=500")
    data = r.json()
    with open("fuel_repos.txt", "w") as f:
        for repo in data['items']:
            f.write("{},{}\n".format(repo['name'], repo['git_url']))

lookup_fuel_repos()
