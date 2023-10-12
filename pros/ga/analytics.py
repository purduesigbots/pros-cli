from configparser import ConfigParser
import sys
import uuid
import time
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
from pros.common.utils import get_version

agent = 'pros-cli'

config = ConfigParser()
config.read('config.ini')


"""
PROS ANALYTICS CLASS
"""

class Analytics():
    def __init__(self):
        from pros.config.cli_config import cli_config as get_cli_config
        self.cli_config = get_cli_config()
        #If GA hasn't been setup yet (first time install/update)
        if not self.cli_config.ga or not self.cli_config.ga.get("unix_timestamp", None):
            
            '''
                We need to ask the user if they want to opt in to analytics. If they do, we generate a UUID for them and a unix timestamp of when they opted in.
                We also need to tell them what we collect, and how they can opt out. This *should* meet some level of GDPR compliance, but I'm not an expert so not positive.
                https://gdpr.eu/gdpr-consent-requirements/ this official page seems to agree. "One easy way to avoid large GDPR fines is to always get permission from your users before using their personal data"

            '''

            print("PROS CLI collects analytics while in use in order to better understand how people use PROS and improve this software. The data collected is as follows:\n    1) Commands being run\n    2) Non identifying command arguments\n    3) Granular location data (through google analytics).")
            print("We do not collect any personal information, or specifics of your projects, file paths, etc.")
            print("You may opt out of analytics at any time by running `pros --use-analytics False`, or may opt out for a single command by adding the `--no-analytics` flag.")
            print("For questions or concerns, please contact us at pros_development@cs.purdue.edu\n")
            response = None
            while response not in ["y", "n"]:
                response = input("Do you choose to opt in to analytics? (y/N): ").lower()

            if response == "y":
                response = "True"
                print("Thank you for opting in to analytics! You may opt out at any time by running `pros --use-analytics False`, or for a specific command by adding the `--no-analytics` flag.")
            else:
                response = "False"
                print("You have opted out of analytics. You may opt back in at any time by running `pros --use-analytics True`.")
            # Default values for GA
            # generate a unix timestamp
            self.cli_config.ga = {
                "enabled": response,
                "unix_timestamp": int(time.time()),
                "u_id": str(uuid.uuid4())
            }
        self.cli_config.save()
        self.sent = False
        #Variables that the class will use
        self.user_timestamp = self.cli_config.ga['unix_timestamp']
        self.useAnalytics = self.cli_config.ga['enabled']
        self.uID = self.cli_config.ga['u_id']
        self.pendingRequests = []

    def send(self, action, kw={}):
        # Send analytics to GA
        if not self.useAnalytics or self.sent:
            return
        
        self.sent = True # Prevent Send from being called multiple times
        try:
            # Copy kw to prevent modifying the original
            kwargs = kw.copy()
            kwargs["engagement_time_msec"] = 1
            kwargs["cli_version"] = get_version()
            kwargs["platform"] = sys.platform
            
            for key, val in kwargs.items():
                # checking for required value
                if val is None:
                    kwargs[key] = "Unspecified_Default"
            key = config['analytics']['api_key']
            url = f'https://www.google-analytics.com/mp/collect?measurement_id=G-PXK9EBVY1Y&api_secret=DRDnqpaeTSebT7BsuGk_oA'
            payload = {
                "client_id": f'CLI.{self.user_timestamp}',
                "user_id": self.uID,
                "non_personalized_ads": True,
                "events": [
                    {
                    "name": action,
                    "params": kwargs
                    }
                ]
            }

            session = FuturesSession()          

            #Send payload to GA servers 
            future = session.post(url=url,
                             data=str(payload).replace("False","false").replace("True","true").replace("Null","null"),
                             timeout=5.0,
                             verify = True)
            self.pendingRequests.append(future)

        except Exception as e:
            from pros.cli.common import logger
            logger(__name__).warning("Unable to send analytics. Do you have a stable internet connection?", extra={'sentry': False})

    def set_use(self, value: bool):
        #Sets if GA is being used or not
        self.useAnalytics = value
        self.cli_config.ga['enabled'] = self.useAnalytics
        self.cli_config.save()
    
    def process_requests(self):
        responses = []
        for future in as_completed(self.pendingRequests):
            try:
                response = future.result()
                #print(response)
                #print(vars(response))
                if not response.status_code==204:
                    print("Something went wrong while sending analytics!")
                    print(response)
                    print(vars(response))
                responses.append(response)

            except Exception:
                print("Something went wrong while sending analytics!")


        self.pendingRequests.clear()
        return responses


analytics = Analytics()