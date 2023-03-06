from enum import Flag, auto


class TemplateAction(Flag):
    NotApplicable = auto()
    Installable = auto()
    Upgradable = auto()
    AlreadyInstalled = auto()
    Downgradable = auto()
    KernelMismatch = auto()

    UnforcedApplicable = Installable | Upgradable | Downgradable
    ForcedApplicable = UnforcedApplicable | AlreadyInstalled


class InvalidTemplateException(Exception):
    def __init__(self, *args, reason: TemplateAction = None):
        self.reason = reason
        super(InvalidTemplateException, self).__init__(*args)

class KernelMismatchException(Exception):
    def __init__(self, *args, reason: TemplateAction = None):
        self.reason = reason
        super(KernelMismatchException, self).__init__(*args)