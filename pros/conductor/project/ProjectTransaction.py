import itertools as it
import os
import tempfile
import zipfile
from typing import *

import pros.common.ui as ui
import pros.conductor as c


class ProjectTransaction(object):
    def __init__(self, project: c.Project, conductor: Optional[c.Conductor] = None):
        self.project = project
        self.conductor = conductor or c.Conductor()
        self.actions = []

    def add_action(self, action: Callable[[c.Conductor, c.Project], Optional[bool]]) -> None:
        self.actions.append(action)

    def execute(self):
        location = self.project.location
        tfd, tfn = tempfile.mkstemp(prefix='pros-project-', suffix=f'-{self.project.name}.zip', text='w+b')
        with os.fdopen(tfd, 'w+b') as tf:
            with zipfile.ZipFile(tf, mode='w') as zf:
                files, length = it.tee(location.glob('**/*'), 2)
                length = len(list(length))
                with ui.progressbar(files, length=length, label=f'Backing up {self.project.name} to {tfn}') as pb:
                    for file in pb:
                        zf.write(file, arcname=file.relative_to(location))

        try:
            with ui.Notification():
                for action in self.actions:
                    ui.logger(__name__).debug(f'Performing {action}')
                    rv = action(self.conductor, self.project)
                    ui.logger(__name__).debug(f'{action} returned {rv}')
                    if rv is not None and not rv:
                        raise ValueError('Action did not complete successfully')
            ui.echo('All actions performed successfully')
        except Exception as e:
            ui.logger(__name__).warning(f'Failed to perform transaction, restoring project to previous state\n'
                                        f'{str(e)}')

            with zipfile.ZipFile(tfn) as zf:
                with ui.progressbar(zf.namelist(), label=f'Restoring {self.project.name} from {tfn}') as pb:
                    for file in pb:
                        zf.extract(file, path=location)

            ui.logger(__name__).exception(e)
        finally:
            ui.echo(f'Removing {tfn}')
            os.remove(tfn)

    def apply_template(self, template: c.BaseTemplate):
        def action(conductor: c.Conductor, p: c.Project) -> Optional[bool]:
            conductor.apply_template(p, template)
            return None

        self.add_action(action)

    def rm_template(self, template: c.BaseTemplate):
        def action(conductor: c.Conductor, p: c.Project) -> Optional[bool]:
            conductor.remove_template(p, template)
            return None

        self.add_action(action)
