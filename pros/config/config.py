import json.decoder
import jsonpickle
import os
import pros.common


class ConfigNotFoundException(Exception):
    def __init__(self, message, *args, **kwargs):
        super(ConfigNotFoundException, self).__init__(args, kwargs)
        self.message = message


class Config(object):
    """
    A configuration object that's capable of being saved as a JSON object
    """
    def __init__(self, file, error_on_decode=False, state=None):
        pros.common.debug('Opening {} ({})'.format(file, self.__class__.__name__), state=state)
        self.save_file = file
        # __ignored property has any fields which shouldn't be included the pickled config file
        self.__ignored = [] if not self.__ignored else self.__ignored
        self.__ignored.append('save_file')
        self.__ignored.append('_Config__ignored')
        if file:
            # If the file already exists, update this new config with the values in the file
            if os.path.isfile(file):
                with open(file, 'r') as f:
                    try:
                        self.__dict__.update(jsonpickle.decode(f.read()).__dict__)
                    except (json.decoder.JSONDecodeError, AttributeError):
                        if error_on_decode:
                            raise
                        else:
                            pass
            # obvious
            elif os.path.isdir(file):
                raise ValueError('{} must be a file, not a directory'.format(file))
            # The file didn't exist when we created, so we'll save the default values
            else:
                try:
                    self.save()
                except Exception as e:
                    pros.common.debug('Failed to save {}: {}'.format(file, e), state=state)

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

    def save(self, file=None, state=None):
        if file is None:
            file = self.save_file
        if pros.common.isdebug(state):
            pros.common.debug('Pretty Formatting {} File'.format(self.__class__.__name__), state=state)
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
