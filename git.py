#!/usr/bin/python

import re
import sys
import subprocess

commit_hash_pattern = '[a-f0-9]{40}'

def log_to_commits(input_file, ticket_match_function):
    commits = []
    commit = None
    for line in input_file:
        match = re.match("^commit (%s)$" % commit_hash_pattern, line)
        if match:
            # commit start
            if commit:
                commits.append(commit)
            commit = { 'id': match.group(1), 'tickets': set() }
        else:
            if commit is None:
                raise ValueError("Unexpected log format: " + repr(line))
            # inside commit
            match = ticket_match_function(line)
            #match = re.match("^ +https?://fedorahosted.org/bind-dyndb-ldap/ticket/([0-9]+) *$",
            #                 line)
            if match:
                commit['tickets'].add(match.group(1))

    if commit:
        commits.append(commit)

    return commits

def text_to_hashes(input_string):
    hashes = set()
    for token in input_string.split():
        match = re.search('(%s)' % commit_hash_pattern, token)
        if match:
            hashes.add(match.group(1))

    return hashes

def commit_contained_in(commit_id):
    process = subprocess.Popen(['/usr/bin/git', 'describe', '--tags', '--contains', str(commit_id)],
                                stdout = subprocess.PIPE)
    out, err = process.communicate()
    if process.returncode != 0:
        raise KeyError("Cannot describe commit " + str(commit_id))

    return out.strip()

def commit_summary(commit_id):
    process = subprocess.Popen(['/usr/bin/git', 'show', '--stat', str(commit_id)],
                                stdout = subprocess.PIPE)
    out, err = process.communicate()
    if process.returncode != 0:
        raise KeyError("Cannot show commit " + str(commit_id))

    return out.strip()
