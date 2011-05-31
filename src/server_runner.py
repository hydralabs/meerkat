"""
"""

import os.path
import sys


try:
    app_name = sys.argv[1]
except IndexError:
    sys.stderr.write('App name required for runner')

    raise SystemExit(1)


base_path = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.join(base_path, 'server')

sys.path.append(app_dir)

full_app_path = os.path.join(app_dir, app_name + '.py')

if not os.path.exists(full_app_path):
    sys.stderr.write('Unknown app name %r' % (app_name,))

    raise SystemExit(1)


app_module = __import__(app_name)


Application = getattr(app_module, 'Application', None)
ServerFactory = getattr(app_module, 'ServerFactory', None)

if not Application:
    sys.stderr.write('%r needs to declare an "Application" class' % (app_name,))

    raise SystemExit(1)

if not ServerFactory:
    from rtmpy.server import ServerFactory


from twisted.internet import reactor
from twisted.python import log


app = Application()


reactor.listenTCP(1935, ServerFactory({
    app_name: app
}))

log.startLogging(sys.stdout)

reactor.run()
