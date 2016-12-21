import os
from pfsense.pfsense import pfSense


class TestClass:

    INCIDENT_IP = "1.1.1.1"
    NONEXISTENT_IP = "256.256.256.256"

    def __init__(self):
        url = os.environ["PFSENSE_URL"]
        password = os.environ["PFSENSE_PASS"]
        self.pf = pfSense(url, password)

    def test_ping(self):
        print "Testing connectivity to pfSense asset"
        assert self.pf.ping()

    def test_block_ip(self):
        print "Testing block ip functionality."
        self.pf.block_ip(self.INCIDENT_IP)
        assert self.pf.rule_exists(self.INCIDENT_IP)

    def test_unblock_ip(self):
        print "Testing unblock ip functionality."
        self.pf.unblock_ip(self.INCIDENT_IP)
        assert self.pf.rule_exists(self.INCIDENT_IP) == False

    def test_rule_exists_nonexistent(self):
        print "Testing rule_exists method against nonexistent rule"
        assert self.pf.rule_exists(self.NONEXISTENT_IP) == False
