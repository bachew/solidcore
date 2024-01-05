from click import argument, group, option, pass_context, pass_obj
from dev import Development, logconf  # TODO: create solidcore, move logconf there
import click
import subprocess


@group('dev', context_settings={
    'show_default': True,
    'help_option_names': ['--help', '-h'],
})
@pass_context
@option('--json', is_flag=True, help='Output log events in json')
@option('-v', 'verbosity',
        default=0,
        count=True,
        help='Logging verbosity, multiple allowed')
def cli(ctx, json, verbosity):
    dev = Development()
    ctx.obj = dev
    logconf.init(json=json)
    logconf.set_verbosity(verbosity)


@cli.command('test-logging')
def cli_test_logging():
    '''
    Test logging with dev -v and --json options.
    '''
    logger_names = [
        'dev',
        # Add logger names you wish to output to console, see also dev.logconf:set_verbosity()
    ]

    for name in logger_names:
        logconf.log_all_levels(name)


@cli.command('run', context_settings={
    'help_option_names': [],
    'ignore_unknown_options': True,
})
@argument('command', nargs=-1, type=click.UNPROCESSED,
          metavar='PROGRAM [ARGS]...')
def cli_run(command):
    '''
    Run a command inside virtual environment.
    '''
    if not command:
        raise click.UsageError('program is required')

    res = subprocess.run(command, check=False)
    raise SystemExit(res.returncode)


@cli.command('lint')
@pass_obj
def cli_lint(dev):
    '''
    Scan code for syntax and typing errors.
    '''
    try:
        dev.lint()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(1)


@cli.command('build')
@pass_obj
def cli_build(dev):
    '''
    Build wheel.
    '''
    dev.build()


@cli.command('upload')
@pass_obj
def cli_upload(dev):
    '''
    Upload wheel to pypi.
    '''
    dev.upload()


cli(prog_name=cli.name)
