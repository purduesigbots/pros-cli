from collections import defaultdict
from typing import *

from pros.common.ui.interactive import components, parameters
from pros.conductor.interactive.parameters import TemplateParameter


class TemplateListingComponent(components.Container):
    def _generate_components(self) -> Generator[components.Component, None, None]:
        if not self.editable['name'] and not self.editable['version']:
            yield components.Label(self.template.value.identifier)
        else:
            if self.editable['name']:
                yield components.InputBox('Name', self.template.name)
            else:
                yield components.Label(self.template.value.name)
            if self.editable['version']:
                if isinstance(self.template.version, parameters.OptionParameter):
                    yield components.DropDownBox('Version', self.template.version)
                else:
                    yield components.InputBox('Version', self.template.version)
            else:
                yield components.Label(self.template.value.version)
        if self.removable:
            remove_button = components.Button('Don\'t remove' if self.template.removed else 'Remove')
            remove_button.on_clicked(lambda: self.template.trigger('removed'))
            yield remove_button

    def __init__(self, template: TemplateParameter,
                 removable: bool = False,
                 editable: Union[Dict[str, bool], bool] = True):
        self.template = template
        self.removable = removable
        if isinstance(editable, bool):
            self.editable = defaultdict(lambda: editable)
        else:
            self.editable = defaultdict(lambda: False)
            if isinstance(editable, dict):
                self.editable.update(**editable)

        super().__init__(*self._generate_components())
