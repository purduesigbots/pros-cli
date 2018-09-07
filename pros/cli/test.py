import os.path
from typing import *

import click

import pros.common.ui.interactive.components as components
import pros.common.ui.interactive.parameters as parameters
from pros.common.ui.interactive.application import Modal
from pros.common.ui.interactive.renderer import MachineOutputRenderer
from pros.conductor import Conductor
from .common import default_options, pros_root


@pros_root
def test_cli():
    pass


def with_click_context(func):
    ctx = click.get_current_context()
    if not ctx:
        return func

    def _wrapper(*args, **kwargs):
        with ctx:
            return func(*args, **kwargs)

    return _wrapper


class NewProjectModal(Modal):
    directory = parameters.Parameter(os.path.expanduser('~'))
    targets = parameters.OptionParameter('v5', ['v5', 'cortex'])

    def __init__(self, conductor=None):
        super().__init__('Create a new project')
        self.conductor = conductor or Conductor()

        self.kernel_versions = parameters.OptionParameter('latest', ['latest'])

        cb = self.targets.on_changed(self.target_changed, asynchronous=True)
        cb(self.targets)

    def target_changed(self, new_target):
        templates = self.conductor.resolve_templates('kernel', target=new_target.value)
        if len(templates) == 0:
            self.kernel_versions.options = parameters.OptionParameter('latest', ['latest'])
        else:
            self.kernel_versions.options = ['latest'] + [t.version for t in templates]
        self.redraw()

    @property
    def can_confirm(self):
        return self.targets.is_valid() and self.kernel_versions.is_valid()

    def confirm(self, *args, **kwargs):
        print(args, kwargs)
        print('confirmed')

    def build(self) -> Generator[components.Component, None, None]:
        yield components.DirectorySelector('Project Directory', self.directory)
        yield components.ButtonGroup('Target', self.targets)
        yield components.DropDownBox('Kernel Version', self.kernel_versions)


@test_cli.command()
@default_options
def test():
    app = NewProjectModal()
    MachineOutputRenderer().run(app)

    # ui.confirm('Hey')
