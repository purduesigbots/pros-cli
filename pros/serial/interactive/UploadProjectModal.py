import os.path
import time
from threading import Thread

from pros.common.utils import with_click_context
from typing import *

import pros.common.ui as ui
from pros.common.ui.interactive import application, parameters, components
from pros.conductor import Project
from pros.conductor.interactive import ExistingProjectParameter
from pros.serial.devices.vex import find_v5_ports, find_cortex_ports
from pros.serial.ports import list_all_comports


class UploadProjectModal(application.Modal):
    def __init__(self):
        super(UploadProjectModal, self).__init__('Upload Project', confirm_button='Upload')

        self.project: Optional[Project] = None
        self.project_path = ExistingProjectParameter(os.path.join(os.path.expanduser('~'), 'My PROS Project'))

        self.port = parameters.OptionParameter('', [''])

        self.slot = parameters.RangeParameter(1, (1, 8))
        self.name = parameters.Parameter('My Project')
        self.description = parameters.Parameter('Created with PROS')

        self.advanced_options_collapsed = parameters.BooleanParameter(True)

        self.alive = True
        self.poll_comports_thread: Optional[Thread] = None

        @self.on_exit
        def cleanup_poll_comports_thread():
            if self.poll_comports_thread is not None and self.poll_comports_thread.is_alive():
                self.alive = False
                self.poll_comports_thread.join()

        cb = self.project_path.on_changed(self.project_changed, asynchronous=True)
        if self.project_path.is_valid():
            cb(self.project_path)

    def update_comports(self):
        list_all_comports.cache_clear()

        if isinstance(self.project, Project):
            options = {}
            if self.project.target == 'v5':
                options = {p.device for p in find_v5_ports('system')}
            elif self.project.target == 'cortex':
                options = [p.device for p in find_cortex_ports()]
            if options != {*self.port.options}:
                self.port.options = list(options)
                if self.port.value not in options:
                    self.port.update(self.port.options[0] if len(self.port.options) > 0 else 'No ports found')
                ui.logger(__name__).debug('Updating ports')
                self.redraw()

    def poll_comports(self):
        while self.alive:
            self.update_comports()
            time.sleep(2)

    def project_changed(self, new_project: ExistingProjectParameter):
        try:
            self.project = Project(new_project.value)

            assert self.project is not None

            self.name.update(self.project.project_name)
            self.slot.update(self.project.upload_options.get('slot', 1))
            self.description.update(self.project.upload_options.get('description', 'Created with PROS'))

            self.update_comports()

            self.redraw()
        except BaseException as e:
            ui.logger(__name__).exception(e)

    def confirm(self, *args, **kwargs):
        pass

    @property
    def can_confirm(self):
        return self.slot.is_valid() and self.project is not None and self.port.is_valid()

    def build(self) -> Generator[components.Component, None, None]:
        if self.poll_comports_thread is None:
            self.poll_comports_thread = Thread(target=with_click_context(self.poll_comports))
            self.poll_comports_thread.start()

        yield components.DirectorySelector('Project Directory', self.project_path)
        yield components.DropDownBox('Port', self.port)

        if isinstance(self.project, Project) and self.project.target == 'v5':
            yield components.Container(
                components.InputBox('Program Name', self.name),
                components.InputBox('Slot', self.slot),
                components.InputBox('Description', self.description),
                title='Advanced V5 Options',
                collapsed=self.advanced_options_collapsed)
