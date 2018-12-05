from enum import Enum


class TemplateAction(Enum):
    NotApplicable = 0
    Installable = 1
    Upgradable = 2
    AlreadyInstalled = 3


class InvalidTemplateException(Exception):
    def __init__(self, *args, reason: TemplateAction = None):
        self.reason = reason
        super(InvalidTemplateException, self).__init__(*args)
