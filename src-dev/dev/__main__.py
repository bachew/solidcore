from click import argument, group, option, pass_context, pass_obj
from dev import Development, logconf
import click
import subprocess


@group('dev', context_settings={
    'show_default': True,
    'help_option_names': ['-h', '--help'],
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
    except subprocess.CalledProcessError:
        raise SystemExit(1)


@cli.command('test', context_settings={
    'ignore_unknown_options': True,
})
@pass_obj
@option('--manual', is_flag=True, help='Include manual tests')
@argument('pytest_args', nargs=-1, type=click.UNPROCESSED)
def cli_test(dev, manual, pytest_args):
    '''
    Run tests. For example:

    \b
      dev test -v

    To run a test case without capturing output:

    \b
      dev test --capture no tests/test_example.py::test_temp_file

    Run 'pytest --help' to see available pytest options like -v and --capture.

    To run a manual test case:

    \b
      dev test --manual tests/test_example.py::test_user_input
    '''
    try:
        dev.test(pytest_args, manual=manual)
    except subprocess.CalledProcessError:
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
    Upload wheel to PyPI.

    To specify credentials, set these environment variables:

    \b
      TWINE_USERNAME
      TWINE_PASSWORD

    To upload to alternate PyPI, set TWINE_REPOSITORY_URL.
    '''
    dev.upload()


cli(prog_name=cli.name)
