import os
import sys

import prosconductor


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
