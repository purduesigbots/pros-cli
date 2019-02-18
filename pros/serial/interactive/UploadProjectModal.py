import os.path
import time
from threading import Thread
from typing import *

import pros.common.ui as ui
from pros.common.ui.interactive import application, components, parameters
from pros.common.utils import with_click_context
from pros.conductor import Project
from pros.conductor.interactive import ExistingProjectParameter
from pros.serial.devices.vex import find_cortex_ports, find_v5_ports
from pros.serial.ports import list_all_comports


class UploadProjectModal(application.Modal[None]):
    def __init__(self, project: Optional[Project]):
        super(UploadProjectModal, self).__init__('Upload Project', confirm_button='Upload')

        self.project: Optional[Project] = project
        self.project_path = ExistingProjectParameter(
            str(project.location) if project else os.path.join(os.path.expanduser('~'), 'My PROS Project')
        )

        self.port = parameters.OptionParameter('', [''])
        self.save_settings = parameters.BooleanParameter(True)
        self.advanced_options: Dict[str, parameters.Parameter] = {}
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

    def update_slots(self):
        assert self.project.target == 'v5'
        if self.port.is_valid() and bool(self.port.value):
            from pros.serial.devices.vex import V5Device
            from pros.serial.ports import DirectPort
            device = V5Device(DirectPort(self.port.value))
            slot_options = [
                f'{slot}' + ('' if program is None else f' (Currently: {program})')
                for slot, program in
                device.used_slots().items()
            ]
        else:
            slot_options = [str(i) for i in range(1, 9)]
        project_name = self.advanced_options['name'].value
        if 'slot' in self.project.upload_options:
            # first, see if the project has it specified in its upload options
            selected = slot_options[self.project.upload_options['slot'] - 1]
        else:
            # otherwise, try to do a name match
            matched_slots = [i for i, slot in enumerate(slot_options) if slot.endswith(f'{project_name})')]
            if len(matched_slots) > 0:
                selected = slot_options[matched_slots[0]]
            elif 'slot' in self.advanced_options:
                # or whatever the last value was
                selected = slot_options[int(self.advanced_options['slot'].value[0]) - 1]
            else:
                # or just slot 1
                selected = slot_options[0]
        self.advanced_options['slot'] = parameters.OptionParameter(
            selected, slot_options
        )

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

                if self.project and self.project.target == 'v5':
                    self.update_slots()

                self.redraw()

    def poll_comports(self):
        while self.alive:
            self.update_comports()
            time.sleep(2)

    def project_changed(self, new_project: ExistingProjectParameter):
        try:
            self.project = Project(new_project.value)

            assert self.project is not None

            if self.project.target == 'v5':
                self.advanced_options = {
                    'name': parameters.Parameter(self.project.upload_options.get('remote_name', self.project.name)),
                    'description': parameters.Parameter(
                        self.project.upload_options.get('description', 'Created with PROS')
                    ),
                    'compress_bin': parameters.BooleanParameter(
                        self.project.upload_options.get('compress_bin', True)
                    )
                }
                self.update_slots()
            else:
                self.advanced_options = {}

            self.update_comports()

            self.redraw()
        except BaseException as e:
            ui.logger(__name__).exception(e)

    def confirm(self, *args, **kwargs):
        from pros.cli.upload import upload
        from click import get_current_context
        kwargs = {'path': None, 'project': self.project, 'port': self.port.value}
        savable_kwargs = {}
        if self.project.target == 'v5':
            savable_kwargs['remote_name'] = self.advanced_options['name'].value
            # XXX: the first character is the slot number
            savable_kwargs['slot'] = int(self.advanced_options['slot'].value[0])
            savable_kwargs['description'] = self.advanced_options['description'].value
            savable_kwargs['compress_bin'] = self.advanced_options['compress_bin'].value

        if self.save_settings.value:
            self.project.upload_options.update(savable_kwargs)
            self.project.save()

        kwargs.update(savable_kwargs)
        self.exit()
        get_current_context().invoke(upload, **kwargs)

    @property
    def can_confirm(self):
        advanced_valid = all(
            p.is_valid()
            for p in self.advanced_options.values()
            if isinstance(p, parameters.ValidatableParameter)
        )
        return self.project is not None and self.port.is_valid() and advanced_valid

    def build(self) -> Generator[components.Component, None, None]:
        if self.poll_comports_thread is None:
            self.poll_comports_thread = Thread(target=with_click_context(self.poll_comports))
            self.poll_comports_thread.start()

        yield components.DirectorySelector('Project Directory', self.project_path)
        yield components.DropDownBox('Port', self.port)
        yield components.Checkbox('Save upload settings', self.save_settings)

        if isinstance(self.project, Project) and self.project.target == 'v5':
            yield components.Container(
                components.InputBox('Program Name', self.advanced_options['name']),
                components.DropDownBox('Slot', self.advanced_options['slot']),
                components.InputBox('Description', self.advanced_options['description']),
                components.Checkbox('Compress Binary', self.advanced_options['compress_bin']),
                title='Advanced V5 Options',
                collapsed=self.advanced_options_collapsed)
