import click
import json.decoder
import jsonpickle
import os.path
import proscli
import proscli.utils
# from typing import List


class ConfigNotFoundException(Exception):
    def __init__(self, message, *args, **kwargs):
        super(ConfigNotFoundException, self).__init__(args, kwargs)
        self.message = message


class Config(object):
    def __init__(self, file, error_on_decode=False, ctx=None):
        proscli.utils.debug('Opening {} ({})'.format(file, self.__class__.__name__), ctx=ctx)
        self.save_file = file   # type: str
        self.__ignored = ['save_file', '_Config__ignored']  # type: list(str)
        if file:
            if os.path.isfile(file):
                with open(file, 'r') as f:
                    try:
                        self.__dict__.update(jsonpickle.decode(f.read()).__dict__)
                    except (json.decoder.JSONDecodeError, AttributeError):
                        if error_on_decode:
                            raise
                        else:
                            pass
            elif os.path.isdir(file):
                raise ValueError('{} must be a file, not a directory'.format(file))
            else:
                try:
                    self.save()
                except Exception:
                    pass

    def __getstate__(self):
        state = self.__dict__.copy()
        if '_Config__ignored' in self.__dict__:
            for key in [k for k in self.__ignored if k in state]:
                del state[key]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def delete(self):
        if os.path.isfile(self.save_file):
            os.remove(self.save_file)

    def save(self, file=None):
        if file is None:
            file = self.save_file
        if isinstance(click.get_current_context().obj, proscli.utils.State) and click.get_current_context().obj.debug:
            proscli.utils.debug('Pretty Formatting {} File'.format(self.__class__.__name__))
            jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
        else:
            jsonpickle.set_encoder_options('json', sort_keys=True)
        if os.path.dirname(file):
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            f.write(jsonpickle.encode(self))

    @property
    def directory(self) -> str:
        return os.path.dirname(os.path.abspath(self.save_file))


class ProjectConfig(Config):
    def __init__(self, path: str='.', create: bool=False, raise_on_error: bool=True):
        file = ProjectConfig.find_project(path or '.')
        if file is None and create:
            file = os.path.join(path, 'project.pros')
        elif file is None and raise_on_error:
            raise ConfigNotFoundException('A project config was not found for {}'.format(path))

        self.kernel = None  # type: str
        self.libraries = []  # type: List[str]
        self.output = 'bin/output.bin'  # type: str
        super(ProjectConfig, self).__init__(file, error_on_decode=raise_on_error)

    @staticmethod
    def find_project(path):
        path = os.path.abspath(path)
        if os.path.isfile(path):
            return path
        elif os.path.isdir(path):
            for n in range(10):
                if path is not None and os.path.isdir(path):
                    files = [f for f in os.listdir(path)
                             if os.path.isfile(os.path.join(path, f)) and f.lower() == 'project.pros']
                    if len(files) == 1:  # found a project.pros file!
                        return os.path.join(path, files[0])
                    path = os.path.dirname(path)
                else:
                    return None
        return None


