from pros.config.config import Config, ConfigNotFoundException
import os.path


class ProjectConfig(Config):
    def __init__(self, path='.', create=False, raise_on_error=True):
        file = ProjectConfig.find_project(path or '.')
        if file is None and create:
            file = os.path.join(path, 'project.pros')
        elif file is None and raise_on_error:
            raise ConfigNotFoundException('A project config was not found for {}'.format(path))

        self.kernel = None  # kernel version
        self.target = None  # VEX Hardware target (V5/Cortex)
        self.libraries = {}
        self.output = 'bin/output.bin'
        self.upload_options = {}
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
