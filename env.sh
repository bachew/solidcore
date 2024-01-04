# env.sh is not executed during bootstrapping, please create env.py instead, for example:
#
#   from os import environ as env
#   from pathlib import Path
#
#
#   base_dir = Path(__file__).parent
#   env['DOCKER_CONFIG'] = str(base_dir / 'tmp/docker-config')
#
#
# Then variables set in env.py will be available in development:
#
# $ bin/dev run python -c 'import os; print(os.environ["DOCKER_CONFIG"])'
