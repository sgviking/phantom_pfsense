# --
# File: pfsense_connector.py
#
# Copyright (c) Dan Daggett
#
# --

import phantom.app as phantom

from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# Imports local to this App
from pfsense_consts import *
from pfsense import *

import datetime


# Define the App Class
class pfSenseConnector(BaseConnector):

    ACTION_ID_BLOCK_IP = "block_ip"
    ACTION_ID_UNBLOCK_IP = "unblock_ip"

    def __init__(self):

        # Call the BaseConnectors init first
        super(pfSenseConnector, self).__init__()

    def initialize(self):
        config = self.get_config()
        server = config.get(PFSENSE_URL)
        password = config.get(PFSENSE_PASSWORD)
        try:
            self.pf = pfSense(server, password)
        except Exception as e:
            return self.set_status_save_progress(phantom.APP_ERROR,
                                                 PFSENSE_ERR_INITIALIZE, e)
        return self.set_status_save_progress(phantom.APP_SUCCESS,
                                             PFSENSE_SUCC_INITIALIZE)

    def _test_connectivity(self, param):

        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES,
                           "Connecting to pfSense asset to check connectivity")

        if pf.ping() == False:
            self.set_status(phantom.APP_ERROR, PFSENSE_ERR_SERVER_CONNECTION, e)
            self.append_to_message(PFSENSE_ERR_CONNECTIVITY_TEST)
            return self.get_status()

        return self.set_status_save_progress(phantom.APP_SUCCESS,
                                             PFSENSE_SUCC_CONNECTIVITY_TEST)

    def _handle_block_ip(self, param):

        config = self.get_config()
        self.debug_print("param", param)

        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        url = config[PFSENSE_URL]
        ip = param[PFSENSE_INCIDENT_IP]

        try:
            self.save_progress(
                "Block IP {} on pfSense asset at {}".format(ip, url))
            self.pf.block_ip(ip)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, PFSENSE_ERR_BLOCK, e)
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, PFSENSE_SUCC_BLOCK)
        return action_result.get_status()

    def _handle_unblock_ip(self, param):

        config = self.get_config()
        self.debug_print("param", param)

        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        url = config[PFSENSE_URL]
        ip = param[PFSENSE_INCIDENT_IP]

        try:
            self.save_progress(
                "Unblock IP {} on pfSense asset at {}".format(ip, url))
            self.pf.unblock_ip(ip)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, PFSENSE_ERR_UNBLOCK, e)
            return action_result.get_status()

        action_result.set_status(phantom.APP_SUCCESS, PFSENSE_SUCC_UNBLOCK)
        return action_result.get_status()

    def handle_action(self, param):

        ret_val = phantom.APP_SUCCESS

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if (action_id == self.ACTION_ID_BLOCK_IP):
            ret_val = self._handle_block_ip(param)
        elif (action_id == self.ACTION_ID_UNBLOCK_IP):
            ret_val = self._handle_unblock_ip(param)
        elif (action_id == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY):
            ret_val = self._test_connectivity(param)

        return ret_val

if __name__ == '__main__':

    import sys
    import pudb
    pudb.set_trace()

    if (len(sys.argv) < 2):
        print "No test json specified as input"
        exit(0)

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = pfSenseConnector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print (json.dumps(json.loads(ret_val), indent=4))

    exit(0)
