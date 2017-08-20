#!/bin/bash

set -x

SCRIPTDIR=$(readlink -f $(dirname $0))
REPOS_FILE=${REPOS_FILE:-${SCRIPTDIR}/fuel_repos.txt}
LOG_FILE=${LOG_FILE:-${SCRIPTDIR}/fetch_repos.log}
GIT_ROOT_PATH=${GIT_ROOT_PATH:-${SCRIPTDIR}/repos}

echo "##################### $(date) #######################"

mkdir -p ${GIT_ROOT_PATH}

cat $REPOS_FILE | while read reponame repourl; do
    pushd ${GIT_ROOT_PATH}
    test -d $reponame || git clone $repourl $reponame
    pushd $reponame
    git fetch -p
    for branch in `git branch -a | grep remotes | grep -v HEAD`; do
        git checkout -b ${branch#remotes/origin/} 2>/dev/null || git checkout ${branch#remotes/origin/}
        git reset --hard $branch
    done
    popd
    popd
done
