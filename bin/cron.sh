#!/bin/bash

DIRECTORY=$(cd `dirname $0` && pwd)

cd $DIRECTORY

cd ../
git pull origin master
python fetch.py
git add ../_posts/
git commit -a -m "Synced RSS feeds"
git push origin master
