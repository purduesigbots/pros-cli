from datetime import datetime, timedelta
from typing import *

import pros.common.ui as ui
from pros.common import logger
from pros.config.cli_config import cli_config
from ..templates import BaseTemplate, Template


class Depot(object):
    def __init__(self, name: str, location: str, config: Dict[str, Any] = None,
                 update_frequency: timedelta = timedelta(minutes=1),
                 config_schema: Dict[str, Dict[str, Any]] = None):
        self.name: str = name
        self.location: str = location
        self.config: Dict[str, Any] = config or {}
        self.config_schema: Dict[str, Dict[str, Any]] = config_schema or {}
        self.remote_templates: List[BaseTemplate] = []
        self.last_remote_update: datetime = datetime(2000, 1, 1)  # long enough time ago to force re-check
        self.update_frequency: timedelta = update_frequency

    def update_remote_templates(self, **_):
        self.last_remote_update = datetime.now()

    def fetch_template(self, template: BaseTemplate, destination: str, **kwargs) -> Template:
        raise NotImplementedError()

    def get_remote_templates(self, auto_check_freq: Optional[timedelta] = None, force_check: bool = False, **kwargs):
        if auto_check_freq is None:
            auto_check_freq = getattr(self, 'update_frequency', cli_config().update_frequency)
        logger(__name__).info(f'Last check of {self.name} was {self.last_remote_update} '
                              f'({datetime.now() - self.last_remote_update} vs {auto_check_freq}).')
        if force_check or datetime.now() - self.last_remote_update > auto_check_freq:
            with ui.Notification():
                ui.echo(f'Updating {self.name}... ', nl=False)
                self.update_remote_templates(**kwargs)
                ui.echo('Done', color='green')
        for t in self.remote_templates:
            t.metadata['origin'] = self.name
        return self.remote_templates
