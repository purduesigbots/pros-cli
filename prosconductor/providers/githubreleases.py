import click
import proscli.utils
from prosconductor.providers import TemplateTypes, DepotProvider, InvalidIdentifierException, DepotConfig, Identifier
import re
import requests
from typing import List, Dict, Set


class GithubReleasesDepotProvider(DepotProvider):
    registrar = 'github-releases'

    def __init__(self, config: DepotConfig):
        super(GithubReleasesDepotProvider, self).__init__(config)

    @staticmethod
    def configure_registar_options():
        options = dict()
        options['include_prerelease'] = click.prompt('Include pre-releases?', default=False, prompt_suffix=' ')
        options['include_draft'] = click.prompt('Include drafts (requires authentication)?',
                                                default=False, prompt_suffix=' ')
        if click.confirm('Do you want to set up OAuth authentication with GitHub?'):
            options['oauth_token'] = click.prompt('OAuth2 Token:', prompt_suffix=' ')
        return options

    def list_all(self, template_types: List[TemplateTypes] = None):
        if not re.fullmatch(pattern='[A-z0-9](?:-?[A-z0-9]){0,38}\/[0-9A-z_\.-]{1,93}', string=self.config.location):
            raise InvalidIdentifierException('{} is an invalid GitHub repository'.format(self.config.location))
        if template_types is None:
            template_types = [TemplateTypes.kernel, TemplateTypes.library]
        config = self.config
        proscli.utils.debug('Fetching listing for {} at {} using {}'.format(config.name, config.location, self.registrar))
        headers = {'user-agent': 'purdueros-cli'}
        if 'oauth_token' in config.registrar_options:
            headers['Authorization'] = 'token {}'.format(config.registrar_options['oauth_token'])
        r = requests.get('https://api.github.com/repos/{}/releases'.format(config.location),
                         headers=headers)
        if r.status_code == 200:
            response = dict()  # type: Dict[TemplateTypes, Set[Identifier]]
            json = r.json()
            # filter out pre-releases according to registar_options (include_prerelease implies prerelease) and
            # by if the release has a kernel-template.zip or library-template.zip file
            for release in [rel for rel in json if
                            (not rel['prerelease'] or config.registrar_options.get('include_prerelease', False)) and
                            (not rel['draft'] or config.registrar_options.get('include_draft', False))]:
                for asset in [a for a in release['assets'] if
                              re.fullmatch(string=a['name'].lower(), pattern='.*-template.zip')]:
                    if asset['name'].lower() == 'kernel-template.zip' and TemplateTypes.kernel in template_types:
                        if TemplateTypes.kernel not in response:
                            response[TemplateTypes.kernel] = set()
                        response[TemplateTypes.kernel].add(Identifier(name='kernel', version=release['tag_name']))
                    elif TemplateTypes.library in template_types:  # if the name is kernel-template.zip, then it's a library
                        if TemplateTypes.library not in response:
                            response[TemplateTypes.library] = set()
                        response[TemplateTypes.library].add(
                            Identifier(name=asset['name'][:-len('-template.zip')], version=release['tag_name']))

            return response
        else:
            click.echo('Unable to get listing for {} at {}'.format(config.name, config.location))
            proscli.utils.debug(r.__dict__)
            return dict()
