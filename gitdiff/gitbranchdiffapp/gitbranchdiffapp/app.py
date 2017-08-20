import os

from flask import Flask
from flask import render_template
from flask import request
import jinja2

from gitbranchdiff import git

from . import settings

app = Flask(__name__, static_folder=settings.STATIC_PATH, static_url_path='')

app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['PROPAGATE_EXCEPTIONS'] = False


jinja_loader = jinja2.ChoiceLoader(
    [jinja2.FileSystemLoader(settings.TEMPLATES_PATH)])
app.jinja_loader = jinja_loader
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

@app.route("/")
def index():
    return render_template('index.html', repos=sorted(git.lookup_git_repos(settings.GIT_ROOT_PATH)))


def _cast_bool(arg):
    if isinstance(arg, (str, unicode)) and arg in ('1', 'true'):
        return True
    return False


def _extended_commits(commits):
    result = {}
    for commit in commits:
        result[commit.branch] = commit
    return result


@app.route("/repodiff/<reponame>", methods=['GET', 'POST'])
def repodiff(reponame):
    # TODO:
    # get repos from database or cache
    # make repos cloud
    repos = sorted(git.lookup_git_repos(settings.GIT_ROOT_PATH))

    repopath = os.path.join(settings.GIT_ROOT_PATH, reponame, ".git")

    if request.method == 'GET':
        branches = sorted(git.lookup_git_branches(repopath, remote=False))
        return render_template(
            'repodiff_form.html',
            reponame=reponame,
            branches=sorted(branches),
            repos=repos)

    elif request.method == 'POST':
        branches = request.form.keys()
        commits = git.git_branch_diff(repopath, branches)
        for change_id in commits:
            commits[change_id] = _extended_commits(commits[change_id])
        return render_template(
            'repodiff.html',
            reponame=reponame,
            branches=sorted(branches),
            commits=commits,
            repos=repos)


def main():
    app.run(host="0.0.0.0")
