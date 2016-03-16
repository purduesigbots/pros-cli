import proscli
import proscli.create
import proscli.upgrade
import proscli.config
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(prog='pros',
                                     description='Interact with PROS projects and VEX microcontrollers.',
                                     epilog='Licensed under the revised BSD License. (c) 2016 Purdue ACM SIGBOTS')
    parser.add_argument('--version', action='version', version='%(prog)s 2.0.beta')
    subparsers = parser.add_subparsers(title='command')
    # <editor-fold desc="conductor subparser">
    conductor_parser = subparsers.add_parser(name='conduct')
    conductor_subparsers = conductor_parser.add_subparsers(title='command')

    # <editor-fold desc="create subparser">
    create_parser = conductor_subparsers.add_parser(name='create', help='Create a PROS Project')
    create_parser.set_defaults(func=proscli.create.command)
    create_parser.add_argument('directory', help='Project directory')
    create_parser.add_argument('--kernel', nargs='?', metavar='KERNEL', default='latest',
                               help="""Specify latest kernel version to target.
                              'latest' defaults to highest locally available kernel.
                              Use 'pros conduct fetch latest' to download latest kernel from update site""")
    create_parser.add_argument('--drop-in', nargs='+', metavar='DROP', default=['none'],
                               help="""Specify extra drop-ins to add to this PROS project.""")
    create_parser.add_argument('-f', '--force', action='store_true',
                               help="""Use this flag to force template files to be copied to directory,
                               even if the directory already exists.""")
    create_parser.add_argument('-v', '--verbose', action='store_true',
                               help="""Use this flag to show verbose output""")
    # </editor-fold>

    # <editor-fold desc="upgrade subparser">
    upgrade_parser = conductor_subparsers.add_parser(name='upgrade', help='Upgrade a PROS Project')
    upgrade_parser.set_defaults(func=proscli.upgrade.command)
    upgrade_parser.add_argument('directory', help='Project directory')
    upgrade_parser.add_argument('--kernel', nargs='?', metavar='KERNEL', default='latest',
                                help="""Specify latest kernel version to target.
                              'latest' defaults to highest locally available kernel.
                              Use 'pros conduct fetch latest' to download latest kernel from update site""")
    upgrade_parser.add_argument('-v', '--verbose', action='store_true',
                                help="""Use this flag to show verbose output""")
    # </editor-fold>

    # <editor-fold desc="config subparser">
    config_parser = conductor_subparsers.add_parser(name='config', help="Configure PROS Conductor")
    config_parser.set_defaults(func=proscli.config.command)
    config_parser.add_argument('variable', help='Relevant variable')
    config_parser.add_argument('value', nargs='?',
                               help="""Optional value to set variable to. If no value is provided,
                               the current stored value will be returned""")
    # </editor-fold>

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_usage()
    else:
        args.func(args)


if __name__ == '__main__':
    main()
