#!/usr/bin/python

import os
import re
import json
import xmlrpclib

class Trac():
    def __init__(self, protocol, url, username, passwd):
        self.baseurl = '%s://%s' % (protocol, url)
        self.username = username
        loginurl = '%s://%s:%s@%s/login/xmlrpc' % (protocol, username, passwd, url)
        self.api = xmlrpclib.ServerProxy(loginurl)
    
    def match_ticket_url(self, line):
        return re.match("^ +%s/ticket/([0-9]+) *$" % self.baseurl, line)

    def get_ticket_attrs(self, ticketid):
        ticket = self.api.ticket.get(ticketid)
        assert str(ticket[0]) == str(ticketid)
        return ticket[3]


if __name__ == "__main__":
    config = json.load(open(os.path.expanduser('~/.trac')))
    t = Trac(**config)
    print t.api
