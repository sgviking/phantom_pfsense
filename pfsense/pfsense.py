#!/usr/bin/env python2.7
# --
# File: pfsense.py
#
# Copyright (c) Dan Daggett
#
# --

import xmlrpclib
import ssl
import datetime
import time
import copy
import os


class pfSense():
    """
    This class is used to interact with a pfSense asset over the XMLRPC
    interface used for syncing pfSense firewalls over a CARP interface.
    This works by downloading a copy of the filter section of the current
    pfSense configuration. Rules are then added or removed to block or unblock
    IP traffic egress on the LAN interface. The modified configuration is then
    restored on the pfSense asset.

    Note: There is a race condition between the time the configuration is pulled
    and when it is pushed back.  Because of this the configuration should be
    pulled right before modification.  In this case it is pulled when the
    block_ip or unblock_ip methods are called.
    """
    _rule_template = {"created": {"time": "", "username": "automation@phantom"},
                      "descr": "Phantom automated rule. Do not edit.",
                      "destination": {},
                      "id": "",
                      "interface": "lan",
                      "ipprotocol": "inet",
                      "max": "",
                      "max-src-conn": "",
                      "max-src-nodes": "",
                      "max-src-states": "",
                      "os": "",
                      "source": {"any": ""},
                      "statetimeout": "",
                      "statetype": "keep state",
                      "tag": "",
                      "tagged": "",
                      "tracker": "",
                      "type": "block",
                      "updated": {"time": "", "username": "automation@phantom"}}

    def __init__(self, url, password):
        self._url = url
        self._password = password
        self._sections = ["filter"]
        self._connect()

    def _connect(self):

        context = hasattr(ssl, "_create_unverified_context") and \
            ssl._create_unverified_context() or None

        if context:
            transport = xmlrpclib.SafeTransport(use_datetime=True,
                                                context=context)
        else:
            transport = xmlrpclib.SafeTransport(use_datetime=True)

        self._server = xmlrpclib.ServerProxy(self._url, transport=transport)
        return True

    def _get_config(self):
        """If this throws an exception it will be handled in the pfsense
        connector class that uses this object."""
        self._config = self._server.pfsense.backup_config_section(
            self._password,
            self._sections
        )
        self._rules = self._config["filter"]["rule"]
        return True

    def _push_config(self):
        """If this throws an exception it will be handled in the pfsense
        connector class that uses this object."""
        self._server.pfsense.restore_config_section(
            self._password,
            self._config
        )
        # apply_rules = \
        #    "pfSense_handle_custom_code('/usr/local/pkg/firewall_rules/apply');"
        # print self._server.pfsense.exec_php(self._password, apply_rules)
        return True

    def rule_exists(self, ip):
        for rule in self._rules:
            if rule["destination"].get("address", None) == ip and \
                    rule["interface"] == "lan" and \
                    rule["descr"].startswith("Phantom automated rule"):
                return True

    def _current_epoch_string(self):
        return str(int(time.mktime(datetime.datetime.now().timetuple())))

    def ping(self):
        """Pull configuration as a test of authenticating and connecting to the
        pfSense asset."""
        try:
            self._get_config()
        except:
            return False
        return True

    def block_ip(self, ip):
        self._get_config()

        if not self.rule_exists(ip):
            lan_rule = copy.deepcopy(self._rule_template)
            lan_rule["created"]["time"] = self._current_epoch_string()
            lan_rule["updated"]["time"] = self._current_epoch_string()
            lan_rule["tracker"] = lan_rule["created"]["time"]
            lan_rule["destination"]["address"] = ip
            self._config["filter"]["rule"].insert(0, lan_rule)

        self._push_config()
        self._get_config()


if __name__ == "__main__":
    try:
        url = os.environ["PFSENSE_URL"]
        password = os.environ["PFSENSE_PASS"]
        ip = os.environ["PFSENSE_INCIDENT_IP"]
    except KeyError:
        print "The PFSENSE_URL, PFSENSE_PASS and PFSENSE_INCIDENT_IP environment variables are required."
        exit(1)

    pf = pfSense(url, password)
    retval = pf.ping()
    print "Ping: {}".format(retval)
    retval = pf.block_ip(ip)
    print "Block IP: {}".format(retval)
    retval = pf.rule_exists(ip)
    print "Rule exists: {}".format(retval)
