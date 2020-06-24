#!/bin/sh

set -e

cd $(dirname $0)/..
git stash save --include-untracked > /dev/null
rsync -azv \
	--exclude '.git*' \
	--exclude .scrapy \
	--exclude __pycache__ \
	--exclude imus/settings.py \
	--exclude imus/logging.yaml \
	--exclude $0 \
	. rpi:imus
git stash pop > /dev/null
