import os
import re

from prosconductor import config


suggested_update_site = "https://raw.githubusercontent.com/purduesigbots/purdueros-kernels/master"


def get_local_kernels():
    if not os.path.exists(config.kernel_repo):
        os.makedirs(config.kernel_repo)
    return [x for x in os.listdir(config.kernel_repo) if not x.startswith('.')]


def resolve_kernel_request(kernel):
    if kernel is None or not kernel or not get_local_kernels():
        return []
    if kernel.lower() == 'all':
        kernel = '.*'
    if kernel.lower() == 'latest':
        return [sorted(get_local_kernels())[-1]]
    else:
        return [x for x in get_local_kernels() if re.match(kernel, x)]


