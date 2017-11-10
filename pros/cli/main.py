import click
import pros.cli.build


def main():
    try:
        cli.main(prog_name='pros')
    except KeyboardInterrupt:
        click.echo('Aborted!')


@click.command('pros',
               cls=click.CommandCollection,
               sources=[pros.cli.build.build_cli])
def cli():
    pass


if __name__ == '__main__':
    main()