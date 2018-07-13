#!/usr/bin/env bash

# JOCA -- Jira On Call Assignee -- Change project lead based on an ical event.
# Copyright (C) 2018 Bryce McNab
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

current_version="v$(grep -E '^    version="[0-9]*\.[0-9]*\.[0-9]*",$' setup.py | awk -F'"' '{print $2}')"
check_for_tag=$(git tag | grep ${current_version})
committed=$(git status | grep "nothing to commit")

if [["${committed}" == ""]];
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
