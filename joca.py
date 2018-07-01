#!/usr/bin/env python
"""
    JOCA -- Jira On Call Assignee -- Change project lead based on an ical event.
    Copyright (C) 2018 Bryce McNab

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import sys
import re
import datetime
import time

try:
    import requests
except ImportError:
    sys.exit(71)

try:
    from icalendar import Calendar
except ImportError:
    sys.exit(71)

try:
    from jira import JIRA
except ImportError:
    sys.exit(71)

def get_current_project_lead(server, username, password, project_key):
    """Polls Jira for the current project lead.

    Args:
        server          str     The URL for the Jira server.
        username        str     Jira username.
        password        str     Jira password.
        project_key     str     Key for the project set of numbers that
                                prepend all issue IDs; i.e. "SUPPORT-1234"
                                has the project key "SUPPORT".
    Returns:
        String: user key.
    """
    jira = JIRA(server, basic_auth=(username, password))
    project = jira.project(project_key.upper())
    current_lead = project.lead.key
    return current_lead

def get_supposed_lead(url, regex, jira_server, jira_username, jira_password, project_key):
    """Downloads current ICS file for parsing.

    Args:
        url             str     URL for the ical file.
        regex           str     Regex string for parsing event
                                subjects.
        server          str     The URL for the Jira server.
        username        str     Jira username.
        password        str     Jira password.
        project_key     str     Key for the project set of numbers that
                                prepend all issue IDs; i.e. "SUPPORT-1234"
                                has the project key "SUPPORT".
    """
    jira = JIRA(jira_server, basic_auth=(jira_username, jira_password))
    cal = Calendar.from_ical(requests.get(url).text)
    for event in cal.walk():
        if event.name == "VEVENT":
            now = time.mktime(datetime.datetime.now().timetuple())
            start = time.mktime(event.get('dtstart').dt.timetuple())
            end = time.mktime(event.get('dtend').dt.timetuple())
            if now > start and now < end:
                supposed_lead = re.search(regex, event.get('summary')).group(1)
    return jira.search_assignable_users_for_projects(supposed_lead, project_key)[0].key

def assign_new_project_lead(server, username, password, project_key, lead):
    """
    Args:
        server          str     The URL for the Jira server.
        username        str     Jira username.
        password        str     Jira password.
        project_key     str     Key for the project set of numbers that
                                prepend all issue IDs; i.e. "SUPPORT-1234"
                                has the project key "SUPPORT".
    """
    update = {
        "key": project_key,
        "lead": lead
    }
    update_project_lead = requests.put(server + "/rest/api/latest/project/" + project_key,
                                        json={"lead": lead},
                                        auth=(username, password))
    if update_project_lead.status_code is 200:
        return True
    else:
        print update_project_lead.status_code
        print update_project_lead.text
        return False

def main():
    """Main function, all work is done here."""
    with open('/etc/joca.conf') as config_data_file:
        config_data_loaded = json.load(config_data_file)
    for project in config_data_loaded['projects']:
        current_lead_key = get_current_project_lead(config_data_loaded['jira']['server'],
                                                    config_data_loaded['jira']['username'],
                                                    config_data_loaded['jira']['password'],
                                                    project['key'])
        supposed_lead_key = get_supposed_lead(project['ical'],
                                              project['regex'],
                                              config_data_loaded['jira']['server'],
                                              config_data_loaded['jira']['username'],
                                              config_data_loaded['jira']['password'],
                                              project['key'])

        if current_lead_key == supposed_lead_key:
            sys.exit(0)
        else:
            assign_new_project_lead(config_data_loaded['jira']['server'],
                                    config_data_loaded['jira']['username'],
                                    config_data_loaded['jira']['password'],
                                    project['key'],
                                    supposed_lead_key)

if __name__ == "__main__":
    main()
