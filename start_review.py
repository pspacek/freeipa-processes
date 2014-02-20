#!/usr/bin/python
import pdb

import os
import sys
import logging
from pprint import pformat

import json
import subprocess
import re

import git
from trac import Trac

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('startreview')

# connect to Trac instance
TRAC_CONF = json.load(open(os.path.expanduser('~/.trac')))
trac = Trac(**TRAC_CONF)

# parse out ticket IDs and commit IDs
commits = git.log_to_commits(sys.stdin, trac.match_ticket_url)

# iterate over tickets mentioned in commits
for commit in commits:
    for ticket in commit['tickets']:
        # get ticket attributes
        attrs = trac.get_ticket_attrs(ticket)
        log.info("Processing ticket %s: %s" % (ticket, attrs['summary']))
        log.debug("Ticket " + str(ticket) + " attributes: " + pformat(attrs))

        # prepare changes in Trac
        trac_changes = {'id': ticket, 'comment': '', 'attributes': {}}
        reviewer = attrs.get('reviewer', '')
        if reviewer:
            log.warn('Reviewer is already set to "%s"' % reviewer)
            continue
        if trac.username not in reviewer:
            trac_changes['attributes']['reviewer'] = trac.username
        if attrs['status'] == 'assigned':
            trac_changes['attributes']['status'] = 'onreview'
        else:
            log.warn('Ticket ' + str(ticket) + ' is not "assigned" but ' + attrs['status'])
            continue

        # do changes
        log.info("Changes in ticket " + str(ticket) + ": " + pformat(trac_changes))
        trac.api.ticket.update(int(trac_changes['id']), trac_changes['comment'], trac_changes['attributes'])

