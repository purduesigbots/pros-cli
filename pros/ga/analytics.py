from os import path
import uuid
import time
from requests_futures.sessions import FuturesSession
import random
from concurrent.futures import as_completed

agent = 'pros-cli'

"""
PROS ANALYTICS CLASS
"""

class Analytics():
    def __init__(self):
        from pros.config.cli_config import cli_config as get_cli_config
        self.cli_config = get_cli_config()
        #If GA hasn't been setup yet (first time install/update)
        if not self.cli_config.ga or not self.cli_config.ga.get("api_secret", None) or not self.cli_config.ga.get("unix_timestamp", None):
            #Default values for GA
            print("helooooo2222222")
            # generate a unix timestamp
            self.cli_config.ga = {
                "enabled": "True",
                "ga_id": "G-PXK9EBVY1Y",
                "api_secret": "VkPGaoemRfygVAXiabM-jg",
                "unix_timestamp": int(time.time()),
                "u_id": str(uuid.uuid4())
            }
        self.cli_config.save()
        self.sent = False
        #Variables that the class will use
        self.gaID = self.cli_config.ga['ga_id']
        self.apiSecret = self.cli_config.ga['api_secret']
        self.user_timestamp = self.cli_config.ga['unix_timestamp']
        self.useAnalytics = self.cli_config.ga['enabled']
        self.uID = self.cli_config.ga['u_id']
        print(f'Analytics config: enabled={self.useAnalytics} | ga_id={self.gaID} | api_secret={self.apiSecret} | u_id={self.uID}')
        self.pendingRequests = []

    def send(self, action, kwargs = {}):
        if not self.useAnalytics or self.sent:
            #print("not sending")
            return
        #print("sending")
        self.sent=True # Prevent Send from being called multiple times
        try:
            kwargs["engagement_time_msec"] = 1
            
            url = f'https://www.google-analytics.com/mp/collect?measurement_id=G-PXK9EBVY1Y&api_secret={self.apiSecret}'
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
            #print(payload)
            #print(url)

            #r = requests.post(url,data=json.dumps(payload),verify=True)
            #print(r.status_code)
            session = FuturesSession()          

            #Send payload to GA servers 
            future = session.post(url=url,
                             data=str(payload).replace("False","false").replace("True","true"),
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