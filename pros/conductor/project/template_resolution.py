from enum import Flag, auto


class TemplateAction(Flag):
    NOT_APPLICABLE = auto()
    INSTALLABLE = auto()
    UPGRADABLE = auto()
    ALREADY_INSTALLED = auto()
    DOWNGRADABLE = auto()

    UNFORCED_APPLICABLE = INSTALLABLE | UPGRADABLE | DOWNGRADABLE
    FORCED_APPLICABLE = UNFORCED_APPLICABLE | ALREADY_INSTALLED


class InvalidTemplateException(Exception):
    def __init__(self, *args, reason: TemplateAction = None):
        self.reason = reason
        super(InvalidTemplateException, self).__init__(*args)
