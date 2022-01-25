import json
from os import path
import uuid
from pros.cli.common import logger

"""
PORTION OF PYGAMP MODULE REQUIRED TO SEND EVENT DATA TO GOOGLE ANALYTICS
INSTALLING PACKAGE WAS NOT WORKING SO JUST COPIED SOURCE CODE
OBTAINED FROM https://github.com/flyandlure/pygamp
"""

import requests
import random

endpoint = 'https://www.google-analytics.com/collect'
user_agent = 'pygamp'


def send(payload, property_id):
    """Send a payload to Google Analytics using the Measurement Protocol API.
    :param payload: Python dictionary of URL key value pairs
    :param property_id: Universal Analytics property ID, i.e. UA-123456-1
    :return: HTTP response status
    """

    required_payload = {
        'v': 1,
        'tid': property_id,
        'aip': 1,
        'z': random.random()
    }

    final_payload = {**required_payload, **payload}
    response = requests.post(url=endpoint,
                             data=final_payload,
                             headers={'User-Agent': user_agent},
                             timeout=5.0)
    print(response.request.body)
    return response

def event(cid,
          property_id: str,
          category: str,
          action: str,
          label: str = None,
          value: int = None,
          non_interactive: int = 0):
    """Create a Google Analytics event using the Measurement Protocol API.
    :param cid: Client ID
    :param property_id: Universal Analytics property ID, i.e. UA-123456-1
    :param category: Event category string
    :param action: Event action string
    :param label: Optional event label string
    :param value: Optional event value integer
    :param non_interactive: Specify whether the hit type is non-interactive by passing 1
    :return: HTTP response status
    """

    payload = {
        'cid': cid,
        't': 'event',
        'ec': category,
        'ea': action,
        'el': label,
        'ev': str(int(value)),
        'ni': non_interactive
    }
    send(payload, property_id)

class Analytics():
    def __init__(self):
        self.uID = str(uuid.uuid4())
        with open(path.join("pros","ga","analytics.json"),"r") as j:
            data = json.load(j)
            self.gaID = data['ga_id']
            self.useAnalytics = True if data['enabled'] == "True" else False
    def send(self,action):
        if not self.useAnalytics:
            return
        try:
            event(
                cid=self.uID,
                property_id=self.gaID,
                category='action',
                action=action,
                label='CLI')
        except Exception as e:
            logger(__name__).exception(e, extra={'sentry': False})

    def set_use(self, value: bool):
        self.useAnalytics = value
        with open(path.join("pros","ga","analytics.json"),"r+") as j:
            data = json.load(j)
            data['enabled'] = str(value)
            j.seek(0)
            json.dump(data,j,indent=4)
            j.truncate()

    def toggle_use(self):
        self.set_use(not self.useAnalytics)
