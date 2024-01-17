# env.sh is not executed during bootstrapping, please create env.py instead, for example with:
#
# from pathlib import Path
# import os
#
#
# base_dir = Path(__file__).parent
# os.environ['DOCKER_CONFIG'] = str(base_dir / 'tmp/docker-config')
#
#
# The variables set in env.py will be available in development, for example:
#
# $ bin/dev run python -c 'import os; print(os.environ["DOCKER_CONFIG"])'
