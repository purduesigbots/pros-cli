import os
import sys

from prosconductor import config, verbosity


class KernelLoader:
    def __init__(self, verbose=0, out=sys.stdout, err=sys.stderr):
        self.__verbose = verbose
        self.__out = out
        self.__err = err

    def create_project(self, kernelpath, projectpath, dropins=[]):
        print('Creating a project at ' + projectpath + ' from ' + kernelpath, file=self.__out)

        if not os.path.exists(projectpath):
            os.makedirs(projectpath)

            # if self.__verbose:
            #     print('Copying files.', file=self.__out)
            # for root, dirs, files in os.walk(kernelpath):
            #     print(root)

    def upgrade_project(self, kernelpath, projectpath, dropins=[]):
        print('Upgrading project at ', projectpath, ' based on ', kernelpath, file=self.__out)

    def list_local_dropins(self, kernelpath):
        if verbosity > 0:
            print('Listing dropins of ', kernelpath)
        if os.path.exists(os.path.join(kernelpath, '=dropins=')):
            return os.listdir(os.path.join(kernelpath, '=dropins='))
        else:
            return []


def find_loader(kernelPath):
    return KernelLoader()


def find_kernel_template(kernel):
    return os.path.join(config.kernel_repo, kernel)


def list_universal_dropins():
    return os.listdir(os.path.join(config.dropin_repo))
