#!/usr/bin/env bash

#git fetch origin
#git reset --hard origin/main

cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd
git pull https://github.com/SamyBarras/stopmotiontoolkit
echo "----- stopmotion tool is now up to date ! ------"