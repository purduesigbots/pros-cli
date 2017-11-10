class DepotProvider(object):
    registrar = 'default-provider'
    location_desc = 'A URL or identifier for a specific depot'
    config = {}

    def __init__(self, config):
        self.config = config

    def list_online(self, template_types=None):
        pass

    def list_latest(self, name):
        """
        :param name:
        :return:
        """
        pass

    def download(self, identifier):
        """
        Downloads the specified template with the given name and version
        :return: True if successful, False if not
        """
        pass

    def verify_configuration(self):
        """
        Verifies the current configuration (i.e. is the location valid)
        :return: Something falsey if valid, an exception (to be raised or displayed)
        """
        pass
