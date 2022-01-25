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