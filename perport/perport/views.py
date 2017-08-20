import collections
import logging
import os
import yaml

from flask import render_template
from flask import request
from flask import redirect
from flask import send_from_directory

from .app import app
from . import objects
from . import utils


LOG = logging.getLogger(__name__)


@app.route("/")
def index():
    menu = {app.idx[id]["name"] : app.idx[id]["url"]
                for id in app.idx["group"]["menu"]}
    return render_template("index.html", menu=menu)


@app.route("/files/<path:filename>")
def file(filename):
    dirname = os.path.dirname(os.path.expanduser(filename))
    basename = os.path.basename(filename)
    return send_from_directory(dirname, basename)


@app.route("/item/<int:id>")
def item(id):
    item = objects.Factory.create(**app.idx[id])
    menu = {app.idx[id]["name"] : app.idx[id]["url"]
                for id in app.idx["group"]["menu"]}
    return render_template("item.html", item=item,
                           tags=utils.group_all_tags(item.group),
                           group=item.group, menu=menu)

@app.route("/<group>")
@app.route("/<group>/<tag>")
def group_tag(group, tag=None):
    ids = app.idx["group"][group]
    if tag is not None:
        ids = app.idx["group"][group] & app.idx["tags"][tag]

    items = (objects.Factory.create(**app.idx[id]) for id in ids)
    menu = {app.idx[id]["name"] : app.idx[id]["url"]
                for id in app.idx["group"]["menu"]}
    return render_template("collection.html", items=items,
                           tags=utils.group_all_tags(app.idx, group),
                           group=group, menu=menu)
