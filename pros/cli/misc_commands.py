import pros.common.ui as ui
from pros.cli.common import *
from pros.ga.analytics import analytics

@pros_root
def set_variable():
    pass

@pros_root
def read_variable():
    pass

@pros_root
def misc_commands_cli():
    pass


@misc_commands_cli.command()
@click.option('--force-check', default=False, is_flag=True,
              help='Force check for updates, disregarding auto-check frequency')
@click.option('--no-install', default=False, is_flag=True,
              help='Only check if a new version is available, do not attempt to install')
@default_options
def upgrade(force_check, no_install):
    """
    Check for updates to the PROS CLI
    """
    analytics.send("upgrade")
    from pros.upgrade import UpgradeManager
    manager = UpgradeManager()
    manifest = manager.get_manifest(force_check)
    ui.logger(__name__).debug(repr(manifest))
    if manager.has_stale_manifest:
        ui.logger(__name__).error('Failed to get latest upgrade information. '
                                  'Try running with --debug for more information')
        return -1
    if not manager.needs_upgrade:
        ui.finalize('upgradeInfo', 'PROS CLI is up to date')
    else:
        ui.finalize('upgradeInfo', manifest)
        if not no_install:
            if not manager.can_perform_upgrade:
                ui.logger(__name__).error(f'This manifest cannot perform the upgrade.')
                return -3
            ui.finalize('upgradeComplete', manager.perform_upgrade())

@set_variable.command(aliases=['sv'])
@default_options
@click.argument('variable', type=click.Choice(['teamnumber', 'robotname']), required=True)
@click.argument('value', required=True, type=click.STRING, nargs=1)
def set_variable(variable, value):
    import pros.serial.devices.vex as vex
    from pros.serial.ports import DirectPort

    # Get the connected v5 device
    port = resolve_v5_port(None, 'system')[0]
    if port == None:
        return
    device = vex.V5Device(DirectPort(port))
    device.kv_write(variable, value)
    ui.finalize('setVariable', f'{variable} set to {value}')

@read_variable.command(aliases=['rv'])
@default_options
@click.argument('variable', type=click.Choice(['teamnumber', 'robotname']), required=True)
def read_variable(variable):
    import pros.serial.devices.vex as vex
    from pros.serial.ports import DirectPort

    # Get the connected v5 device
    port = resolve_v5_port(None, 'system')[0]
    if port == None:
        return
    device = vex.V5Device(DirectPort(port))
    value = device.kv_read(variable)
    print(value)
    ui.finalize('readVariable', f'{variable}\'s read value is {value}')
    