"""
"""

import os.path
import shutil

import buildmeta



def options(ctx):
    """
    """
    gr = ctx.add_option_group('Server target `py_server`',
        'Options for testing with RTMPy acting as a server.')



def configure(ctx):
    """
    """
    ctx.load('python')
    ctx.check_python_module('rtmpy')



def build(ctx):
    """
    Builds a number of python scripts that can be run from the commandline.
    """
    build_runner(ctx)
    build_apps(ctx)



def build_apps(ctx):
    """
    """
    tests = buildmeta.get_tests(ctx)

    server_build_node = ctx.path.find_or_declare('python/server')

    for f in ctx.path.ant_glob('src/suite/**/python/server.py'):
        rel_path = f.srcpath()

        split_path = rel_path.split(os.path.sep)
        test_namespace = split_path[2:-2]
        module = '_'.join(test_namespace)
        c = tests.add('py_server', module)

        app_node = server_build_node.find_or_declare(module + '.py')

        try:
            os.unlink(app_node.abspath())
        except OSError:
            pass

        try:
            shutil.copy2(f.abspath(), app_node.abspath())
        except OSError:
            ctx.fatal('Unable to copy python server app %r (path:%r)' % (
                module, app_node.bldpath()))

        c['file'] = app_node.bldpath()
        c['module'] = module



def build_runner(ctx):
    """
    Copy the runner
    """
    src = ctx.path.find_node('src/server_runner.py')
    dest = ctx.path.find_or_declare('python/runner.py')

    try:
        os.unlink(dest.abspath())
    except OSError:
        pass

    try:
        shutil.copy2(src.abspath(), dest.abspath())
    except OSError:
        ctx.fatal('Unable to copy python runner to %r' % (dest.bldpath(),))

    try:
        os.chmod(dest.abspath(), 0755)
    except OSError:
        ctx.fatal('Unable to create executable python runner at %r' % (
            dest.bldpath(),))
