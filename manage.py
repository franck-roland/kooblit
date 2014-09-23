#!/bin/bash

"true" '''\' This shebang is here to ensure that we use the venv python in all cases.
# So we use bash as the base script, then figure out which python to use, and run
# this script again. We use the 'true' command because it ignores its argument.
exec "$(dirname $0)/env/bin/python" "$0" "$@"
'''

import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kooblit.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
