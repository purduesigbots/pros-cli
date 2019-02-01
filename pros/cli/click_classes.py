from collections import defaultdict
from typing import *

import click.decorators


class PROSFormatted(click.BaseCommand):
    """
    Common format functions used in the PROS derived classes. Derived classes mix and match which functions are needed
    """

    def __init__(self, *args, hidden: bool = False, **kwargs):
        super(PROSFormatted, self).__init__(*args, **kwargs)
        self.hidden = hidden

    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
                after the options.
                """
        if not hasattr(self, 'list_commands'):
            return
        rows = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if hasattr(cmd, 'hidden') and cmd.hidden:
                continue

            help = cmd.short_help or ''
            rows.append((subcommand, help))

        if rows:
            with formatter.section('Commands'):
                formatter.write_dl(rows)

    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        opts: DefaultDict[str, List] = defaultdict(lambda: [])
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                if hasattr(param, 'group'):
                    opts[param.group].append(rv)
                else:
                    opts['Options'].append(rv)

        if len(opts['Options']) > 0:
            with formatter.section('Options'):
                formatter.write_dl(opts['Options'])
            opts.pop('Options')

        for group, options in opts.items():
            with formatter.section(group):
                formatter.write_dl(options)

        self.format_commands(ctx, formatter)


class PROSCommand(PROSFormatted, click.Command):
    pass


class PROSMultiCommand(PROSFormatted, click.MultiCommand):
    def get_command(self, ctx, cmd_name):
        super().get_command(ctx, cmd_name)


class PROSOption(click.Option):
    def __init__(self, *args, hidden: bool = False, group: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hidden = hidden
        self.group = group

    def get_help_record(self, ctx):
        if hasattr(self, 'hidden') and self.hidden:
            return
        return super().get_help_record(ctx)


class PROSGroup(PROSFormatted, click.Group):
    def __init__(self, *args, **kwargs):
        super(PROSGroup, self).__init__(*args, **kwargs)
        self.cmd_dict = dict()

    def command(self, *args, aliases=None, **kwargs):
        aliases = aliases or []

        def decorator(f):
            for alias in aliases:
                self.cmd_dict[alias] = f.__name__ if len(args) == 0 else args[0]

            cmd = super(PROSGroup, self).command(*args, cls=kwargs.pop('cls', PROSCommand), **kwargs)(f)
            self.add_command(cmd)
            return cmd

        return decorator

    def group(self, aliases=None, *args, **kwargs):
        aliases = aliases or []

        def decorator(f):
            for alias in aliases:
                self.cmd_dict[alias] = f.__name__
            cmd = super(PROSGroup, self).group(*args, cls=kwargs.pop('cls', PROSGroup), **kwargs)(f)
            self.add_command(cmd)
            return cmd

        return decorator

    def get_command(self, ctx, cmd_name):
        # return super(PROSGroup, self).get_command(ctx, cmd_name)
        suggestion = super(PROSGroup, self).get_command(ctx, cmd_name)
        if suggestion is not None:
            return suggestion
        if cmd_name in self.cmd_dict:
            return super(PROSGroup, self).get_command(ctx, self.cmd_dict[cmd_name])

        # fall back to guessing
        matches = {x for x in self.list_commands(ctx) if x.startswith(cmd_name)}
        matches.union({x for x in self.cmd_dict.keys() if x.startswith(cmd_name)})
        if len(matches) == 1:
            return super(PROSGroup, self).get_command(ctx, matches.pop())
        return None


class PROSRoot(PROSGroup):
    pass


class PROSCommandCollection(PROSFormatted, click.CommandCollection):
    pass
