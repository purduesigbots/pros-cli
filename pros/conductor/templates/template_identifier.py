import os.path
import re

TEMPLATE_REGEX = r"([^\\/]+)[\\/]([^\\/-]+)-([^\\/]+)"


class TemplateIdentifier(object):
    def __new__(cls, value):
        def apply(depot, name, version):
            cls.name = name
            cls.version = version
            cls.depot = depot

        if isinstance(value, TemplateIdentifier):
            apply(value.depot, value.name, value.version)
        elif isinstance(value, str): # deduce the meaning
            match = re.fullmatch(TEMPLATE_REGEX, value)
            if match is not None:
                apply(match.group(1), match.group(2), match.group(3))
            elif os.path.exists(value):
                if os.path.isfile(value):
                    value = os.path.dirname(value)
                if os.path.isdir(value):
                    value = os.path.join(os.path.split(value)[-2])
                    match = re.fullmatch(TEMPLATE_REGEX, os.path.join(value.split(os.sep)[-2:]))
                    if match is not None:
                        apply(match.group(1), match.group(2), match.group(3))
        elif isinstance(value, tuple) or isinstance(value, list):
            if len(value) == 1:
                cls.__new__(cls, value[0])
            elif len(value) == 2:
                apply(None, value[0], value[1])
            elif len(value) == 3:
                apply(value[0], value[1], value[2])
            else:
                raise ValueError('Couldn\'t deduce meaning of {}'.format(value))
        else:
            raise ValueError('Couldn\'t deduce meaning of {}'.format(value))
        return super(TemplateIdentifier, cls).__new__(cls)

    def __str__(self):
        if self.depot:
            return '{}/{}-{}'.format(self.depot, self.name, self.version)
        else:
            return '{}-{}'.format(self.name, self.version)

    def __hash__(self):
        return self.__str__()
