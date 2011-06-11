"""
"""

import subprocess
import signal
import os.path
import sys
import time
import shutil


from tests import tests


FLASH_PLAYER = '{{ FLASH_PLAYER }}'
JAVA = '{{ JAVA }}'
SIKULI_HOME = '{{ SIKULI_HOME }}'
SIKULI_SCRIPT = SIKULI_HOME + '/sikuli-script.jar'
SIKULI_RUNNER = 'runner.sikuli'


# proxy settings
LOCAL_SERVER = '{{ LOCAL_SERVER }}'
REMOTE_SERVER = '{{ REMOTE_SERVER }}'

OUTPUT_DIR = 'output'


def run_py_server(**context):
    """
    Run a python server and return a handle to the subprocess
    """
    args = ['python/runner.py', context['module']]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.poll() is not None:
        # we died
        raise RuntimeError('Stuff went boom')

    return p


def run_swf(**context):
    """
    Fire up the Sikuli runner
    """
    args = [JAVA, '-jar', SIKULI_SCRIPT, SIKULI_RUNNER, FLASH_PLAYER, context['file']]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return p



def run_proxy(file):
    """
    """
    args = ['./proxy.py', LOCAL_SERVER, REMOTE_SERVER, file]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.poll() is not None:
        # we died
        raise RuntimeError('Proxy went boom')

    return p



class Result(object):
    """
    """

    def __init__(self, parent, name, context):
        self.parent = parent
        self.name = name
        self.context = context


    def setServerPipes(self, pipes):
        self.server_pipes = pipes


    def setClientPipes(self, pipes):
        self.client_pipes = pipes


    def setProxyPipes(self, pipes):
        self.proxy_pipes = pipes


    def finish(self):
        self.parent.finish(self.name)


    def error(self):
        self.parent.addError(self)


    def success(self):
        self.parent.addSuccess(self)


    def failure(self):
        self.parent.addFailure(self)


    def timeout(self):
        self.parent.addTimeout(self)


    def unexpectedError(self):
        self.parent.addUnexpectedError(self)


    def nomatch(self):
        self.parent.addUnexpectedError(self)



class ResultSet(object):
    """
    """

    verbose = False
    passed = True

    def __init__(self):
        self.results = {}
        self.meta_results = {}
        self._currentResult = None


    def start(self, name):
        if self._currentResult is not None:
            raise RuntimeError('Test %r is still running' % (self._currentResult,))

        os.mkdir(os.path.join(OUTPUT_DIR, name))
        self._currentResult = name
        context = self.results[name] = {}
        r = Result(self, name, context)

        context['start'] = time.time()

        print name, '...', 

        return r


    def recordResult(self, name, result):
        """
        """
        base_path = os.path.join(OUTPUT_DIR, name, '')

        cp = result['proxy_pipes']

        with open(base_path + 'proxy.stdout', 'w+') as o:
            o.write('\n'.join(cp['stdout']))

        with open(base_path + 'proxy.stderr', 'w+') as o:
            o.write('\n'.join(cp['stderr']))

        cp = result['client_pipes']

        with open(base_path + 'client.stdout', 'w+') as o:
            o.write('\n'.join(cp['stdout']))

        with open(base_path + 'client.stderr', 'w+') as o:
            o.write('\n'.join(cp['stderr']))

        cp = result['server_pipes']

        with open(base_path + 'server.stdout', 'w+') as o:
            o.write('\n'.join(cp['stdout']))

        with open(base_path + 'server.stderr', 'w+') as o:
            o.write('\n'.join(cp['stderr']))


    def _setStatus(self, status, meta_result, result):
        """
        """
        r = self.results[self._currentResult]

        r['status'] = status
        r['proxy_pipes'] = result.proxy_pipes
        r['client_pipes'] = result.client_pipes
        r['server_pipes'] = result.server_pipes

        try:
            self.meta_results[meta_result] += 1
        except KeyError:
            self.meta_results[meta_result] = 1


    def addSuccess(self, result):
        self._setStatus('success', 'successes', result)

        print 'PASS'


    def addFailure(self, result):
        self.passed = False

        self._setStatus('failure', 'failures', result)

        print 'FAIL'


    def addError(self, result):
        self.passed = False

        self._setStatus('error', 'errors', result)

        print 'ERROR'


    def addUnexpectedError(self, result):
        self.passed = False

        self._setStatus('error', 'errors', result)

        print 'ERROR?!'


    def addTimeout(self, result):
        self.passed = False

        self._setStatus('timeout', 'timeouts', result)

        print 'TIMEOUT'


    def finish(self, name):
        assert name == self._currentResult

        r = self.results[name]

        r['finish'] = time.time()

        if r['status'] == 'success' and not self.verbose:
            shutil.rmtree(os.path.join(OUTPUT_DIR, name))
        else:
            self.recordResult(self._currentResult, r)

        self._currentResult = None


    def report(self):
        print

        print '=' * 80
        print 'Ran %d tests' % len(self.results)
        print

        if self.passed:
            print 'PASSED',
        else:
            print 'FAILED',


        print '(%s)' % ', '.join(['%s=%d' % (k, v) for k, v in self.meta_results.items()])


def get_sikuli_result(stdout):
    """
    Return the test result from sikuli
    """
    for l in stdout:
        if l.startswith('RESULT: '):
            return l.rsplit('RESULT: ')[-1].strip()


# main program execution here

results = ResultSet()

server_type = sys.argv[1]
client_type = sys.argv[2]


run_server = globals()['run_' + server_type]
run_client = globals()['run_' + client_type]

ordered = sorted(tests.keys())

try:
    os.mkdir(OUTPUT_DIR)
except:
    shutil.rmtree(OUTPUT_DIR)

    os.mkdir(OUTPUT_DIR)


for name in ordered:
    context = tests[name]

    server_context = context[server_type]
    client_context = context[client_type]

    test = results.start(name)

    proxy_process = run_proxy(os.path.join(OUTPUT_DIR, name, name + '.carrays'))
    server_process = run_server(**server_context)
    client_process = run_client(**client_context)

    client_process.wait()
    server_process.terminate()
    proxy_process.send_signal(signal.SIGINT)
    proxy_process.wait()

    client_pipes = {
        'stdout': client_process.stdout.read().strip().split('\n'),
        'stderr': client_process.stderr.read().strip().split('\n')
    }

    server_pipes = {
        'stdout': server_process.stdout.read().strip().split('\n'),
        'stderr': server_process.stderr.read().strip().split('\n')
    }

    proxy_pipes = {
        'stdout': proxy_process.stdout.read().strip().split('\n'),
        'stderr': proxy_process.stderr.read().strip().split('\n')
    }

    result = get_sikuli_result(client_pipes['stdout'])

    test.setServerPipes(server_pipes)
    test.setClientPipes(client_pipes)
    test.setProxyPipes(proxy_pipes)

    if result is None:
        test.unexpectedError()
    else:
        # call the correct method on the test object
        getattr(test, result)()

    test.finish()


results.report()

if not results.passed:
    sys.exit(1)
