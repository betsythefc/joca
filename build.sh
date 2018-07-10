#!/usr/bin/env bash

current_version="v$(grep -E '^    version="[0-9]*\.[0-9]*\.[0-9]*",$' setup.py | awk -F'"' '{print $2}')"
check_for_tag=$(git tag | grep ${current_version})
committed=$(git status | grep "nothing to commit")

if ["${committed}" == ""];
then
    echo "Commit your changes!"
    exit
fi

if ["${check_for_tag}" != ""];
then
    last_commit=$(git log --name-status HEAD^..HEAD | head -1 | awk '{print $2}')
    git tag -a ${current_version} ${last_commit} -m "${current_version}"
    git push origin ${current_version}
fi

python setup.py sdist bdist_wheel upload
