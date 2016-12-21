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

import simplejson as json
import datetime


def _json_fallback(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj


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

        # Get the config
        config = self.get_config()

        self.debug_print("param", param)

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)
#
#        # get the server
#        server = config.get(SAMPLEWHOIS_JSON_SERVER)
#
#        domain = param[SAMPLEWHOIS_JSON_DOMAIN]
#
#        try:
#            if (server):
#                self.save_progress("Using Server {0}".format(server))
#                raw_whois_resp = pythonwhois.net.get_whois_raw(domain, server)
#                whois_response = pythonwhois.parse.parse_raw_whois(raw_whois_resp)
#            else:
#                self.save_progress("Using default root Server")
#                whois_response = pythonwhois.get_whois(domain)
#        except Exception as e:
#            action_result.set_status(phantom.APP_ERROR, SAMPLEWHOIS_ERR_QUERY, e)
#            return action_result.get_status()
#
#        # Need to work on the json, it contains certain fields that are not
#        # parsable, so will need to go the 'fallback' way.
#        # TODO: Find a better way to do this
#        whois_response = json.dumps(whois_response, default=_json_fallback)
#        whois_response = json.loads(whois_response)
#        action_result.add_data(whois_response)
#
#        # Even if the query was successfull the data might not be available
#        if (self._response_no_data(whois_response, domain)):
#            return action_result.set_status(phantom.APP_ERROR, SAMPLEWHOIS_ERR_QUERY_RETURNED_NO_DATA)
#
#        # get the registrant
#        if ('contacts' in whois_response and 'registrant' in whois_response['contacts']):
#            registrant = whois_response['contacts']['registrant']
#            wanted_keys = ['organization', 'city', 'country']
#            summary = {x: registrant.get(x, '') for x in wanted_keys}
#            action_result.update_summary(summary)
#            action_result.set_status(phantom.APP_SUCCESS)
#        else:
#            action_result.set_status(phantom.APP_SUCCESS, SAMPLEWHOIS_SUCC_QUERY)
        action_result.set_status(phantom.APP_SUCCESS, PFSENSE_SUCC_QUERY)
        return action_result.get_status()

    def _handle_unblock_ip(self, param):
        config = self.get_config()
        self.debug_print("param", param)
        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)
        action_result.set_status(phantom.APP_SUCCESS, PFSENSE_SUCC_QUERY)
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
