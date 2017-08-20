import collections
import os
import re
import yaml


class IndexManager(object):

    IDX_FIELDS = ("group", "date", "tags")
    IDX_REGEX = ".*\.yaml"

    def __init__(self, index_dir):
        self.index_dir = index_dir
        self.idx = None

    def init(self):
        self.idx = {"ALL": set()}
        for field in self.IDX_FIELDS:
            self.idx[field] = collections.defaultdict(set)
        self._read_index()
        self._build_fields()

    def _read_index(self):
        inc_id = 0
        regex = re.compile(self.IDX_REGEX)
        for root, dirs, files in os.walk(self.index_dir):
            for file in files:
                if regex.match(file):
                    with open(os.path.join(root, file)) as f:
                        for item in yaml.safe_load(f):
                            if not "id" in item:
                                item["id"], inc_id = inc_id, inc_id + 1
                            self.idx[item["id"]] = item
                            self.idx["ALL"].add(item["id"])

    def _build_fields(self):
        for id in self.idx["ALL"]:
            item = self.idx[id]
            for field in self.IDX_FIELDS:
                if field in item:
                    if isinstance(item[field], list):
                        for value in item[field]:
                            self.idx[field][value].add(id)
                    else:
                        value = item[field]
                        self.idx[field][value].add(id)
