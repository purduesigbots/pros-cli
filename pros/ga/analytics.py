import json
from os import path
import uuid
import requests
import random

url = 'https://www.google-analytics.com/collect'
agent = 'pros-cli'

"""
PROS ANALYTICS CLASS
"""

class Analytics():
    def __init__(self):
        self.sent = False
        data = self.read_json()
        self.gaID = data['ga_id']
        self.useAnalytics = True if data['enabled'] == "True" else False
        data['u_id'] = str(uuid.uuid4()) if data['u_id'] == "None" else data['u_id']
        self.uID = data['u_id']
        self.save_json(data)


    def send(self,action):
        if not self.useAnalytics or self.sent:
            return
        self.sent=True # Prevent Send from being called multiple times
        try:
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
                'ni': 0
            }           
            response = requests.post(url=url,
                             data=payload,
                             headers={'User-Agent': agent},
                             timeout=5.0)
            if not response.status_code==200:
                print("Something went wrong while sending analytics!")
                print(response)
            return response
        except Exception as e:
            from pros.cli.common import logger
            logger(__name__).exception(e, extra={'sentry': False})

    def set_use(self, value: bool):
        self.useAnalytics = value
        data = self.read_json()
        data['enabled'] = str(value)
        self.save_json(data)

    def save_json(self, data):
        with open(path.join(__file__.replace(".py",".json")),"r+") as j:
            j.seek(0)
            json.dump(data,j,indent=4)
            j.truncate()

    def read_json(self):
        with open(path.join(__file__.replace(".py",".json")),"r") as j: 
            data = json.load(j)
            return data

    def toggle_use(self):
        self.set_use(not self.useAnalytics)

analytics = Analytics()