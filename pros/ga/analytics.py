from pygamp import event
import json
import uuid
from pros.cli.common import logger

class Analytics():
    def __init__(self):
        self.uID = uuid(uuid.uuid4())
        with open("analytics.json","r") as j:
            data = json.load(j)
            self.gaID = data['ga_id']
            self.useAnalytics = data['enabled']

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
        with open("keys.json","w+") as j:
            data = json.load(j)
            data['enabled'] = value
            j.seek(0)
            json.dump(data,j,indent=4)
            j.truncate()

    def toggle_use(self):
        self.set_use(not self.useAnalytics)
