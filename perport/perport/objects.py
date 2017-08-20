import codecs
import os

import misaka


class FileMarkdown(object):
    def __init__(self, **kwargs):
        self.group = kwargs["group"]
        self.path = os.path.expanduser(kwargs["path"])
        self.date = kwargs.get("date")
        self.tags = kwargs.get("tags", [])

    def render(self):
        md = misaka.Markdown(misaka.HtmlRenderer(),
                             extensions=('fenced-code','tables', 'math',))
        with codecs.open(self.path, mode="r", encoding="utf-8") as f:
            return md(f.read())


class Factory(object):
    typemap = {
        "file/markdown": FileMarkdown,
    }

    @classmethod
    def create(cls, **kwargs):
        return cls.typemap.get(kwargs["type"])(**kwargs)
