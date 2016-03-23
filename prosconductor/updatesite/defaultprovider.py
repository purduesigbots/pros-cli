class DefaultUpdateSiteProvider:
    def claims_uri(self, uri):
        return False

    def reform_uri(self, uri):
        return uri

    def can_handle_uri(self, uri):
        return True

    def get_available_kernels(self, uri):
        return []

    def get_latest_kernel(self, uri):
        return ''

    def get_available_dropins(self, uri):
        return []

    def download_kernel(self, uri, kernel):
        pass

    def download_dropin(self, uri, dropin):
        pass
