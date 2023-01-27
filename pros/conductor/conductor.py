import os.path
import shutil
from pathlib import Path
from typing import *

import click
from semantic_version import Spec, Version

from pros.common import *
from pros.conductor.project import TemplateAction
from pros.conductor.project.template_resolution import InvalidTemplateException
from pros.config import Config
from .depots import Depot, HttpDepot
from .project import Project
from .templates import BaseTemplate, ExternalTemplate, LocalTemplate, Template

MAINLINE_NAME = 'pros-mainline'
MAINLINE_URL = 'https://purduesigbots.github.io/pros-mainline/pros-mainline.json'


class Conductor(Config):
    """
    Provides entrances for all conductor-related tasks (fetching, applying, creating new projects)
    """

    def __init__(self, file=None):
        if not file:
            file = os.path.join(click.get_app_dir('PROS'), 'conductor.pros')
        self.local_templates: Set[LocalTemplate] = set()
        self.depots: Dict[str, Depot] = {}
        self.default_target: str = 'v5'
        self.default_libraries: Dict[str, List[str]] = None
        super(Conductor, self).__init__(file)
        needs_saving = False
        if MAINLINE_NAME not in self.depots or \
                not isinstance(self.depots[MAINLINE_NAME], HttpDepot) or \
                self.depots[MAINLINE_NAME].location != MAINLINE_URL:
            self.depots[MAINLINE_NAME] = HttpDepot(MAINLINE_NAME, MAINLINE_URL)
            needs_saving = True
        if self.default_target is None:
            self.default_target = 'v5'
            needs_saving = True
        if self.default_libraries is None:
            self.default_libraries = {
                'v5': ['okapilib'],
                'cortex': []
            }
            needs_saving = True
        if 'v5' not in self.default_libraries:
            self.default_libraries['v5'] = []
            needs_saving = True
        if 'cortex' not in self.default_libraries:
            self.default_libraries['cortex'] = []
            needs_saving = True
        if needs_saving:
            self.save()

        from pros.common.sentry import add_context
        add_context(self)

    def get_depot(self, name: str) -> Optional[Depot]:
        return self.depots.get(name)

    def fetch_template(self, depot: Depot, template: BaseTemplate, **kwargs) -> LocalTemplate:
        for t in list(self.local_templates):
            if t.identifier == template.identifier:
                self.purge_template(t)

        if 'destination' in kwargs:  # this is deprecated, will work (maybe) but not desirable behavior
            destination = kwargs.pop('destination')
        else:
            destination = os.path.join(self.directory, 'templates', template.identifier)
            if os.path.isdir(destination):
                shutil.rmtree(destination)

        template: Template = depot.fetch_template(template, destination, **kwargs)
        click.secho(f'Fetched {template.identifier} from {depot.name} depot', dim=True)
        local_template = LocalTemplate(orig=template, location=destination)
        local_template.metadata['origin'] = depot.name
        click.echo(f'Adding {local_template.identifier} to registry...', nl=False)
        self.local_templates.add(local_template)
        self.save()
        if isinstance(template, ExternalTemplate) and template.directory == destination:
            template.delete()
        click.secho('Done', fg='green')
        return local_template

    def purge_template(self, template: LocalTemplate):
        if template not in self.local_templates:
            logger(__name__).info(f"{template.identifier} was not in the Conductor's local templates cache.")
        else:
            self.local_templates.remove(template)

        if os.path.abspath(template.location).startswith(
                os.path.abspath(os.path.join(self.directory, 'templates'))) \
                and os.path.isdir(template.location):
            shutil.rmtree(template.location)
        self.save()

    def resolve_templates(self, identifier: Union[str, BaseTemplate], allow_online: bool = True,
                          allow_offline: bool = True, force_refresh: bool = False,
                          unique: bool = True, **kwargs) -> List[BaseTemplate]:
        results = list() if not unique else set()
        kernel_version = kwargs.get('kernel_version', None)
        if isinstance(identifier, str):
            query = BaseTemplate.create_query(name=identifier, **kwargs)
        else:
            query = identifier
        if allow_offline:
            offline_results = filter(lambda t: t.satisfies(query, kernel_version=kernel_version), self.local_templates)
            if unique:
                results.update(offline_results)
            else:
                results.extend(offline_results)
        if allow_online:
            for depot in self.depots.values():
                online_results = filter(lambda t: t.satisfies(query, kernel_version=kernel_version),
                                        depot.get_remote_templates(force_check=force_refresh, **kwargs))
                if unique:
                    results.update(online_results)
                else:
                    results.extend(online_results)
            logger(__name__).debug('Saving Conductor config after checking for remote updates')
            self.save()  # Save self since there may have been some updates from the depots
        return list(results)

    def resolve_template(self, identifier: Union[str, BaseTemplate], **kwargs) -> Optional[BaseTemplate]:
        if isinstance(identifier, str):
            kwargs['name'] = identifier
        elif isinstance(identifier, BaseTemplate):
            kwargs['orig'] = identifier
        query = BaseTemplate.create_query(**kwargs)
        logger(__name__).info(f'Query: {query}')
        logger(__name__).debug(query.__dict__)
        templates = self.resolve_templates(query, **kwargs)
        logger(__name__).info(f'Candidates: {", ".join([str(t) for t in templates])}')
        if not any(templates):
            return None
        query.version = str(Spec(query.version or '>0').select([Version(t.version) for t in templates]))
        v = Version(query.version)
        v.prerelease = v.prerelease if len(v.prerelease) else ('',)
        v.build = v.build if len(v.build) else ('',)
        query.version = f'=={v}'
        logger(__name__).info(f'Resolved to {query.identifier}')
        templates = self.resolve_templates(query, **kwargs)
        if not any(templates):
            return None
        # prefer local templates first
        local_templates = [t for t in templates if isinstance(t, LocalTemplate)]
        if any(local_templates):
            # there's a local template satisfying the query
            if len(local_templates) > 1:
                # This should never happen! Conductor state must be invalid
                raise Exception(f'Multiple local templates satisfy {query.identifier}!')
            return [t for t in templates if isinstance(t, LocalTemplate)][0]

        # prefer pros-mainline template second
        mainline_templates = [t for t in templates if t.metadata['origin'] == 'pros-mainline']
        if any(mainline_templates):
            return mainline_templates[0]

        # No preference, just FCFS
        return templates[0]

    def apply_template(self, project: Project, identifier: Union[str, BaseTemplate], **kwargs):
        upgrade_ok = kwargs.get('upgrade_ok', True)
        install_ok = kwargs.get('install_ok', True)
        downgrade_ok = kwargs.get('downgrade_ok', True)
        download_ok = kwargs.get('download_ok', True)
        force = kwargs.get('force_apply', False)

        kwargs['target'] = project.target
        if 'kernel' in project.templates:
            # support_kernels for backwards compatibility, but kernel_version should be getting most of the exposure
            kwargs['kernel_version'] = kwargs['supported_kernels'] = project.templates['kernel'].version
        template = self.resolve_template(identifier=identifier, allow_online=download_ok, **kwargs)
        if template is None:
            raise dont_send(
                InvalidTemplateException(f'Could not find a template satisfying {identifier} for {project.target}'))

        if not isinstance(template, LocalTemplate):
            with ui.Notification():
                template = self.fetch_template(self.get_depot(template.metadata['origin']), template, **kwargs)
        assert isinstance(template, LocalTemplate)

        logger(__name__).info(str(project))
        valid_action = project.get_template_actions(template)
        if valid_action == TemplateAction.NotApplicable:
            raise dont_send(
                InvalidTemplateException(f'{template.identifier} is not applicable to {project}', reason=valid_action)
            )
        if force \
                or (valid_action == TemplateAction.Upgradable and upgrade_ok) \
                or (valid_action == TemplateAction.Installable and install_ok) \
                or (valid_action == TemplateAction.Downgradable and downgrade_ok):
            project.apply_template(template, force_system=kwargs.pop('force_system', False),
                                   force_user=kwargs.pop('force_user', False),
                                   remove_empty_directories=kwargs.pop('remove_empty_directories', False))
            ui.finalize('apply', f'Finished applying {template.identifier} to {project.location}')
        else:
            raise dont_send(
                InvalidTemplateException(f'Could not install {template.identifier} because it is {valid_action.name},'
                                         f' and that is not allowed.', reason=valid_action)
            )

    @staticmethod
    def remove_template(project: Project, identifier: Union[str, BaseTemplate], remove_user: bool = True,
                        remove_empty_directories: bool = True):
        ui.logger(__name__).debug(f'Uninstalling templates matching {identifier}')
        for template in project.resolve_template(identifier):
            ui.echo(f'Uninstalling {template.identifier}')
            project.remove_template(template, remove_user=remove_user,
                                    remove_empty_directories=remove_empty_directories)

    def new_project(self, path: str, no_default_libs: bool = False, **kwargs) -> Project:
        if Path(path).exists() and Path(path).samefile(os.path.expanduser('~')):
            raise dont_send(ValueError('Will not create a project in user home directory'))
        proj = Project(path=path, create=True)
        if 'target' in kwargs:
            proj.target = kwargs['target']
        if 'project_name' in kwargs and kwargs['project_name'] and not kwargs['project_name'].isspace():
            proj.project_name = kwargs['project_name']
        else:
            proj.project_name = os.path.basename(os.path.normpath(os.path.abspath(path)))
        if 'version' in kwargs:
            if kwargs['version'] == 'latest':
                kwargs['version'] = '>=0'
            self.apply_template(proj, identifier='kernel', **kwargs)
        proj.save()

        if not no_default_libs:
            for library in self.default_libraries[proj.target]:
                try:
                    # remove kernel version so that latest template satisfying query is correctly selected
                    if 'version' in kwargs:
                        kwargs.pop('version')
                    self.apply_template(proj, library, **kwargs)
                except Exception as e:
                    logger(__name__).exception(e)
        return proj
