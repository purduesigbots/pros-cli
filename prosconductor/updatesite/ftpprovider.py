from prosconductor.updatesite.genericprovider import UpdateSiteProvider


class FtpProvider(UpdateSiteProvider):
    @staticmethod
    def get_key():
        return 'ftp'
