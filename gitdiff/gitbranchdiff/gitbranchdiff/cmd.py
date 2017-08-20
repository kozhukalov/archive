import argparse
import os
import sys

from . import config
from . import git
from . import parse


config.DEBUG = False

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--repopath', action='store', required=True,
                        help='Full path to a repository including .git. '
                        'E.g. /home/user/repo/.git')

    parser.add_argument('--branches', action='store', nargs='+', type=str,
                        help='Branches to inspect. There could be multiple '
                        'branches. E.g. --branches master stable/newton')

    params, other_params = parser.parse_known_args()
    if params.branches is None:
        params.branches = ['master']
    return params.repopath, params.branches


def esq(s):
    return s.replace('"', '\\\\"')

def commit_csv(commit):
    if commit is None:
        return ",,,,,,"
    commit_template = ',"{branch}","{sha}","{title}","{author}","{udate}","{bugs}"'
    bugs = []
    for ref_type, ref in commit.parsed.get('refs', []):
        if ref_type in ('closes-bug', 'related-bug', 'partial-bug'):
            bug_id = ref.replace('https://bugs.launchpad.net/fuel/+bug/', '')
            bugs.append(
                'https://bugs.launchpad.net/fuel/+bug/{}'.format(bug_id))
    commit_str = commit_template.format(
        branch=commit.branch, sha=commit.sha[:8], title=esq(commit.title),
        author=commit.author, udate=commit.udate, bugs=" ".join(bugs))
    return commit_str

def _extended_commits(commits, branches):
    result = []
    for branch in branches:
        try:
            commit = next((c for c in commits if c.branch == branch))
        except StopIteration:
            commit = None
        result.append(commit)
    return result

def csvdiff():
    repopath, branches = parse_args()
    reponame = os.path.basename(os.path.dirname(repopath))
    change_id_index = git.git_branch_diff(repopath, branches)
    for change_id, commits in change_id_index.iteritems():
        csv = "{},https://review.openstack.org/#/q/{}".format(
            reponame, change_id)
        commits = _extended_commits(commits, branches)
        for commit in commits:
            csv += commit_csv(commit)
        print csv
