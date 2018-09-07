import os
import shutil
from typing import *

import pros.common.ui as ui
from pros.common import logger


class Transaction(object):
    def __init__(self, location: str, current_state: Set[str]):
        self._add_files: Set[str] = set()
        self._rm_files: Set[str] = set()
        self._add_srcs: Dict[str, str] = {}
        self.effective_state = current_state
        self.location: str = location

    def extend_add(self, paths: Iterable[str], src: str):
        for path in paths:
            self.add(path, src)

    def add(self, path: str, src: str):
        path = os.path.normpath(path.replace('\\', '/'))
        self._add_files.add(path)
        self.effective_state.add(path)
        self._add_srcs[path] = src
        if path in self._rm_files:
            self._rm_files.remove(path)

    def extend_rm(self, paths: Iterable[str]):
        for path in paths:
            self.rm(path)

    def rm(self, path: str):
        path = os.path.normpath(path.replace('\\', '/'))
        self._rm_files.add(path)
        if path in self.effective_state:
            self.effective_state.remove(path)
        if path in self._add_files:
            self._add_files.remove(path)
            self._add_srcs.pop(path)

    def commit(self, label: str = 'Committing transaction', remove_empty_directories: bool = True):
        with ui.progressbar(length=len(self._rm_files) + len(self._add_files), label=label) as pb:
            for file in sorted(self._rm_files, key=lambda p: p.count('/') + p.count('\\'), reverse=True):
                file_path = os.path.join(self.location, file)
                if os.path.isfile(file_path):
                    logger(__name__).info(f'Removing {file}')
                    os.remove(os.path.join(self.location, file))
                else:
                    logger(__name__).info(f'Not removing nonexistent {file}')
                pardir = os.path.abspath(os.path.join(file_path, os.pardir))
                while remove_empty_directories and len(os.listdir(pardir)) == 0:
                    logger(__name__).info(f'Removing {os.path.relpath(pardir, self.location)}')
                    os.rmdir(pardir)
                    pardir = os.path.abspath(os.path.join(pardir, os.pardir))
                    if pardir == self.location:
                        # Don't try and recursively delete folders outside the scope of the
                        # transaction directory
                        break
                pb.update(1)
            for file in self._add_files:
                source = os.path.join(self._add_srcs[file], file)
                destination = os.path.join(self.location, file)
                if os.path.isfile(source):
                    if not os.path.isdir(os.path.dirname(destination)):
                        logger(__name__).debug(f'Creating directories: f{destination}')
                        os.makedirs(os.path.dirname(destination), exist_ok=True)
                    logger(__name__).info(f'Adding {file}')
                    shutil.copy(os.path.join(self._add_srcs[file], file), os.path.join(self.location, file))
                else:
                    logger(__name__).info(f"Not copying {file} because {source} doesn't exist.")
                pb.update(1)

    def __str__(self):
        return f'Transaction Object: ADD: {self._add_files}\tRM: {self._rm_files}\tLocation: {self.location}'
