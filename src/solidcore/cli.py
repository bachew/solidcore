from click import group
import click
import solidcore


@group(context_settings={
    'show_default': True,
    'help_option_names': ['-h', '--help'],
})
@click.version_option(solidcore.__version__)
def cli():
    pass


@cli.command('hi')
def cli_hi():
    print('Hi!')
