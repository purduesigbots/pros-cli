from .utils import *


def confirm(text, default=False, abort=False, prompt_suffix=': ',
            show_default=True, err=False):
    if ismachineoutput():
        pass
    else:
        return click.confirm(text, default=default, abort=abort, prompt_suffix=prompt_suffix,
                             show_default=show_default, err=err)


def prompt(text, default=None, hide_input=False,
           confirmation_prompt=False, type=None,
           value_proc=None, prompt_suffix=': ',
           show_default=True, err=False):
    if ismachineoutput():
        # TODO
        pass
    else:
        return click.prompt(text, default=default, hide_input=hide_input, confirmation_prompt=confirmation_prompt,
                            type=type, value_proc=value_proc, prompt_suffix=prompt_suffix, show_default=show_default,
                            err=err)
