import argparse
import logging
import os
import sys
import re
import collections
import itertools

from flask import Flask
import jinja2
import yaml

from . import index

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC_PATH = os.path.join(ROOT_PATH, "static")
TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "templates")


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app = Flask(__name__, static_folder=STATIC_PATH,
            static_url_path="/static")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index-dir", dest="index_dir", type=str,
                        required=True, help="Index directory")
    args, unknown = parser.parse_known_args()

    app.config["DEBUG"] = True
    app.config["TESTING"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = False

    jinja_loader = jinja2.ChoiceLoader(
        [jinja2.FileSystemLoader(TEMPLATES_PATH)])
    app.jinja_loader = jinja_loader
    app.jinja_env.add_extension("jinja2.ext.loopcontrols")

    imanager = index.IndexManager(args.index_dir)
    imanager.init()

    app.idx = imanager.idx

    from . import views

    app.run(host="0.0.0.0")
