import json
import random
import uuid
from concurrent.futures import as_completed
from os import path

import requests
from requests_futures.sessions import FuturesSession

url = 'https://www.google-analytics.com/collect'
agent = 'pros-cli'

"""
PROS ANALYTICS CLASS
"""


class Analytics:
    def __init__(self):
        from pros.config.cli_config import cli_config as get_cli_config

        self.cli_config = get_cli_config()
        # If GA hasn't been setup yet (first time install/update)
        if not self.cli_config.ga:
            # Default values for GA
            self.cli_config.ga = {"enabled": "True", "ga_id": "UA-84548828-8", "u_id": str(uuid.uuid4())}
        self.cli_config.save()
        self.sent = False
        # Variables that the class will use
        self.gaID = self.cli_config.ga['ga_id']
        self.useAnalytics = self.cli_config.ga['enabled']
        self.uID = self.cli_config.ga['u_id']
        self.pendingRequests = []

    def send(self, action):
        if not self.useAnalytics or self.sent:
            return
        self.sent = True  # Prevent Send from being called multiple times
        try:
            # Payload to be sent to GA, idk what some of them are but it works
            payload = {
                'v': 1,
                'tid': self.gaID,
                'aip': 1,
                'z': random.random(),
                'cid': self.uID,
                't': 'event',
                'ec': 'action',
                'ea': action,
                'el': 'CLI',
                'ev': '1',
                'ni': 0,
            }

            session = FuturesSession()

            # Send payload to GA servers
            future = session.post(url=url, data=payload, headers={'User-Agent': agent}, timeout=5.0)
            self.pendingRequests.append(future)

        except Exception:
            from pros.cli.common import logger

            logger(__name__).warning(
                "Unable to send analytics. Do you have a stable internet connection?", extra={'sentry': False}
            )

    def set_use(self, value: bool):
        # Sets if GA is being used or not
        self.useAnalytics = value
        self.cli_config.ga['enabled'] = self.useAnalytics
        self.cli_config.save()

    def process_requests(self):
        responses = []
        for future in as_completed(self.pendingRequests):
            try:
                response = future.result()

                if not response.status_code == 200:
                    print("Something went wrong while sending analytics!")
                    print(response)

                responses.append(response)

            except Exception:
                print("Something went wrong while sending analytics!")

        self.pendingRequests.clear()
        return responses


analytics = Analytics()
