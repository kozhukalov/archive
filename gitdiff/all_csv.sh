#!/bin/bash

set -x

DIFFDIR=/home/ubuntu/diffs
REPOSDIR=/home/ubuntu/utilities/repos
BRANCHES="master stable/newton stable/mitaka"

if [ -d $DIFFDIR ]; then
   echo "$DIFFDIR already exists. Please choose another directory" 1>&2
   exit 1
fi

mkdir -p $DIFFDIR

for repo in $(ls -1 $REPOSDIR); do
    repopath=$REPOSDIR/$repo/.git
    gitbranchdiff-csv --repopath $repopath --branches $BRANCHES > $DIFFDIR/$repo.csv 2>/dev/null
done

find $DIFFDIR -type f -empty -delete
