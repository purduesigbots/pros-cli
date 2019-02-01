import os.path


class ProjectReport(object):
    def __init__(self, project: 'Project'):
        self.project = {
            "target": project.target,
            "location": os.path.abspath(project.location),
            "name": project.name,
            "templates": [{"name": t.name, "version": t.version, "origin": t.origin} for t in
                          project.templates.values()]
        }

    def __str__(self):
        import tabulate
        s = f'PROS Project for {self.project["target"]} at: {self.project["location"]}' \
            f' ({self.project["name"]})' if self.project["name"] else ''
        s += '\n'
        rows = [t.values() for t in self.project["templates"]]
        headers = [h.capitalize() for h in self.project["templates"][0].keys()]
        s += tabulate.tabulate(rows, headers=headers)
        return s

    def __getstate__(self):
        return self.__dict__
