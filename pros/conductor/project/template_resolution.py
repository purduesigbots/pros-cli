from enum import Enum


class TemplateAction(Enum):
    NotApplicable = 0
    Installable = 1
    Upgradable = 2
    AlreadyInstalled = 3


class InvalidTemplateException(Exception):
    pass
