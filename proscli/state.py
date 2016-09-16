import prosconfig.cliconfig


class State(object):
    def __init__(self):
        self.verbosity = 0
        self.debug = False
        self.machine_output = False
        self.log_key = 'pros-logging'
        self.pros_cfg = prosconfig.cliconfig.CliConfig(ctx=self)
