from pros.common.ui.interactive.parameters.misc_parameters import OptionParameter
from .component import BasicParameterizedComponent


class DropDownBox(BasicParameterizedComponent[OptionParameter]):
    def __getstate__(self):
        return dict(
            **super(DropDownBox, self).__getstate__(),
            options=self.parameter.options
        )


class ButtonGroup(DropDownBox):
    pass
