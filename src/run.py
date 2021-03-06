"""
Run a server and client target that has been built by waf. Acts like a standard
Python test runner.

Exit status of non zero if the test run did not pass.
"""

import subprocess
import os.path
import sys
import time
import shutil


from tests import tests


CLIENT_TARGET = '{{ CLIENT_TARGET }}'
SERVER_TARGET = '{{ SERVER_TARGET }}'

FLASH_PLAYER = '{{ FLASH_PLAYER }}'
JAVA = '{{ JAVA }}'
SIKULI_HOME = '{{ SIKULI_HOME }}'
SIKULI_SCRIPT = SIKULI_HOME + '/sikuli-script.jar'
SIKULI_RUNNER = 'runner.sikuli'


# proxy settings
LOCAL_SERVER = '{{ LOCAL_SERVER }}'
REMOTE_SERVER = '{{ REMOTE_SERVER }}'

OUTPUT_DIR = 'output'


# fms
FMS_HOST = '{{ FMS_HOST }}'
FMS_USER = '{{ FMS_USER }}'
FMS_PASSWD = '{{ FMS_PASSWD }}'


def run_fms(**context):
    """
    Unload the app that is about to be tested
    """
    url = ('http://%(FMS_HOST)s:1111/admin/restartVHost?auser=%(FMS_USER)s&apswd=%(FMS_PASSWD)s&vhost=%(FMS_HOST)s' % globals())

    # TODO: Fix this hack in FMS
    url2 = ('http://%(FMS_HOST)s:1111/admin/restartVHost?auser=%(FMS_USER)s&apswd=%(FMS_PASSWD)s&vhost=localhost' % globals())

    import urllib2

    r = urllib2.urlopen(url)
    r2 = urllib2.urlopen(url2)

    response = r.read()
    response2 = r2.read()

    assert 'NetConnection.Call.Success' in response
    assert 'NetConnection.Call.Success' in response2

    class EmptyStream(object):
        def read(self):
            return ''


    class MyPOpen(object):
        """
        Pretend to act like a subprocess.POpen instance
        """

        stdout = EmptyStream()
        stderr = EmptyStream()

        def terminate(self):
            pass


    return MyPOpen()

    

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



def run(*test_labels):
    results = ResultSet()

    run_server = globals()['run_' + SERVER_TARGET]
    run_client = globals()['run_' + CLIENT_TARGET]

    ordered = sorted(tests.keys())

    tests_to_run = test_labels

    if not tests_to_run:
        tests_to_run = ordered
    else:
        t = []

        for i in tests_to_run:
            if i in ordered:
                t.append(i)

        tests_to_run = t

    try:
        os.mkdir(OUTPUT_DIR)
    except:
        shutil.rmtree(OUTPUT_DIR)

        os.mkdir(OUTPUT_DIR)


    for name in tests_to_run:
        context = tests[name]

        server_context = context[SERVER_TARGET]
        client_context = context[CLIENT_TARGET]

        test = results.start(name)

        proxy_process = run_proxy(os.path.join(OUTPUT_DIR, name, name + '.carrays'))
        server_process = run_server(**server_context)
        client_process = run_client(**client_context)

        client_process.wait()
        server_process.terminate()
        proxy_process.terminate()

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

    return results



if __name__ == '__main__':
    results = run(*sys.argv[1:])

    results.report()

    if not results.passed:
        raise SystemExit(1)
