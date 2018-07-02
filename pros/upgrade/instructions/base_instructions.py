class UpgradeResult(object):
    def __init__(self, successful: bool, **kwargs):
        self.successful = successful
        self.__dict__.update(**kwargs)

    def __str__(self):
        return f'The upgrade was {"" if self.successful else "not "}successful.\n{getattr(self, "explanation", "")}'


class UpgradeInstruction(object):
    """
    Base class for all upgrade instructions, not useful to instantiate
    """

    def perform_upgrade(self) -> UpgradeResult:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()
