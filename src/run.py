"""
"""

import subprocess
import time
import sys


from tests import tests


FLASH_PLAYER = 'Flash Player Debugger'
JAVA = '/usr/bin/java'
SIKULI_HOME = '/Applications/Sikuli-IDE.app/Contents/Resources/Java'
SIKULI_SCRIPT = SIKULI_HOME + '/sikuli-script.jar'
SIKULI_RUNNER = 'runner.sikuli'


def run_py_server(**context):
    """
    Run a python server and return a handle to the subprocess
    """
    p = subprocess.Popen(['python/runner.py', context['module']])

    if p.poll() is not None:
        # we died
        raise RuntimeError('Stuff went boom')

    return p


def run_swf(**context):
    """
    Fire up the Sikuli runner
    """
    p = subprocess.Popen([JAVA, '-jar', SIKULI_SCRIPT, SIKULI_RUNNER, FLASH_PLAYER, context['file']])

    return p



server_type = sys.argv[1]
client_type = sys.argv[2]


run_server = globals()['run_' + server_type]
run_client = globals()['run_' + client_type]

ordered = sorted(tests.keys())


for name in ordered:
    context = tests[name]

    server_context = context[server_type]
    client_context = context[client_type]

    server_process = run_server(**server_context)
    client_process = run_client(**client_context)

    client_process.wait()
    server_process.terminate()
