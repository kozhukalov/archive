import collections
import datetime
import logging
import os
import string
import sys

import pygit2

from . import config
from . import parse


LOG = logging.getLogger(__name__)


class Commit(object):
    def __init__(self, pygit_commit, branch=None):
        self.pygit_commit = pygit_commit
        self.sha = str(self.pygit_commit.oid)
        self.date = None
        self.udate = None
        self.author = None
        self.title = None
        self.change_id = None
        self.branch = branch
        self.parsed = {}

    def parse(self):
        try:
            self.parsed.update(
                parse.parse_commit_message(self.pygit_commit.message))
        except TypeError:
            LOG.warn("There was an error while parsing "
                     "commit message for %s", self.sha)
        try:
            # print "refs: %s" % self.parsed.get('refs')
            self.change_id = next(
                (ref[1] for ref in self.parsed.get('refs', [])
                 if ref[0] == "change-id"))
        except StopIteration:
            LOG.warn("There is no change-id ref in commit %s", self.sha)

        self.date = str(datetime.datetime.fromtimestamp(
            self.pygit_commit.commit_time))
        self.udate = self.pygit_commit.commit_time
        self.author = self.pygit_commit.author.name.encode('utf-8')
        self.title = self.parsed.get('title')


class CommitCollection(object):
    def __init__(self):
        self.collection = set()

    def add(self, commit):
        self.collection.add(commit)

    def filter_out(self, filter_lambda):
        for commit in self.collection.copy():
            if filter_lambda(commit):
                self.collection.remove(commit)

    def map(self, map_lambda):
        for commit in self.collection:
            map_lambda(commit)

    # def stored_index(self, index_name, index_lambda):
    #     pass

    def index(self, index_lambda):
        idx = collections.defaultdict(set)
        for commit in self.collection:
            idx[index_lambda(commit)].add(commit)
        return idx


def git_branch_diff(repopath, branches):
    repo = pygit2.Repository(repopath)
    commits = CommitCollection()

    LOG.debug("Collecting all commits into dict")
    for branch in branches:
        oid = repo.lookup_branch(branch).target
        for commit in (Commit(c, branch) for c in
                       repo.walk(oid, pygit2.GIT_SORT_TIME)):
            commits.add(commit)

    LOG.debug("Creating sha index over all commits")
    sha_index = commits.index(lambda x: x.sha)

    LOG.debug("Filtering out those commits which are present in all branches")
    commits.filter_out(
        lambda x: set((c.branch for c in sha_index[x.sha])) == set(branches))

    LOG.debug("Parsing commit messages for all commits")
    commits.map(lambda x: getattr(x, 'parse')())

    LOG.debug("Filtering out those commits which do not have Change-Id")
    # It makes sense if only commits are parsed
    commits.filter_out(lambda x: x.change_id is None)

    LOG.debug("Creating change_id index over all commits")
    change_id_index = commits.index(lambda x: x.change_id)

    commits.filter_out(
        lambda x: set((c.branch for c in change_id_index[x.change_id]))
        == set(branches))
    change_id_index = commits.index(lambda x: x.change_id)

    def minimal_udate(commits):
        return sorted([c.udate for c in commits])[0]

    LOG.debug("Sorting change_id index by minimal date "
              "of all commits with this Change-Id")
    return collections.OrderedDict(
        sorted(change_id_index.items(), key=lambda x: minimal_udate(x[1])))


def lookup_git_repos(rootpath):
    for item in os.listdir(rootpath):
        itemdir = os.path.join(rootpath, item)
        try:
            if os.path.isdir(itemdir) and ".git" in os.listdir(itemdir):
                yield item
        except OSError:
            pass


def lookup_git_branches(repopath, local=True, remote=True):
    repo = pygit2.Repository(repopath)
    flag = 0
    if local:
        flag |= pygit2.GIT_BRANCH_LOCAL
    if remote:
        flag |= pygit2.GIT_BRANCH_REMOTE
    return repo.listall_branches(flag)
