import os
import random
import urllib.request, urllib.error, urllib.parse
from zipfile import ZipFile

import sys

import prosconductor
from prosconductor.updatesite import DefaultUpdateSiteProvider


class UrlUpdateSiteProvider(DefaultUpdateSiteProvider):
    def claims_uri(self, uri):
        return False

    def reform_uri(self, uri):
        return uri

    def can_handle_uri(self, uri):
        try:
            result = urllib.request.urlopen(urllib.parse.urljoin('{0}/'.format(uri), './kernels.list'))
            result.read().decode()
            return True
        except UnicodeDecodeError as e:
            if prosconductor.verbosity > 1:
                print('Error decoding response. Response MIME is', result.info()['content-type'], file=sys.stderr)
            return False
        except urllib.error.URLError as e:
            if prosconductor.verbosity > 1:
                print(e.reason, file=sys.stderr)
            return False
        except urllib.error.HTTPError as e:
            if prosconductor.verbosity > 0:  # lower verbosity level since error messages are typically more user friendly
                print(e.code, file=sys.stderr)
            return False

    def get_available_kernels(self, uri):
        try:
            return urllib.request.urlopen(urllib.parse.urljoin(uri + '/', './kernels.list')).read().decode().split()
        except (urllib.error.URLError, urllib.error.HTTPError, UnicodeDecodeError) as e:
            print(uri + ' -> ' + str(e))
            return []

    def get_latest_kernel(self, uri):
        try:
            return urllib.request.urlopen(urllib.parse.urljoin(uri + '/', './latest.kernel')).read().decode()
        except (urllib.error.URLError, urllib.error.HTTPError, UnicodeDecodeError):
            return []

    def get_available_dropins(self, uri):
        try:
            return urllib.request.urlopen(urllib.parse.urljoin(uri + '/', './dropins.list')).read().decode()
        except (urllib.error.URLError, urllib.error.HTTPError, UnicodeDecodeError):
            return []

    def download_dropin(self, uri, dropin):
        temp = os.path.join(prosconductor.config.dropin_repo,
                            '{dropin}_{hash:05X}.zip'.format(dropin=dropin, hash=random.getrandbits(20)))
        urllib.request.urlretrieve(urllib.parse.urljoin(uri + '/', './dropins/' + dropin + '.zip'), temp)
        ZipFile(temp).extractall(path=os.path.join(prosconductor.config.dropin_repo, dropin))
        os.remove(temp)

    def download_kernel(self, uri, kernel):
        temp = os.path.join(prosconductor.config.kernel_repo,
                            '{kernel}_{hash:05X}.zip'.format(kernel=kernel, hash=random.getrandbits(20)))
        urllib.request.urlretrieve(urllib.parse.urljoin(uri + '/', './' + kernel + '.zip'), temp)
        ZipFile(temp).extractall(path=os.path.join(prosconductor.config.kernel_repo, kernel))
        os.remove(temp)
