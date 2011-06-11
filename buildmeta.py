"""
"""

import sys
import os.path
import shutil
from urlparse import urlparse


class TestContainer(dict):
    """
    """

    def __init__(self, d):
        self.update(d)

    def add(self, type, name):
        return self.setdefault(name, {}).setdefault(type, {})



def clear_test_file(ctx):
    """
    """
    n = ctx.path.find_or_declare('tests.py')

    n.delete()



def get_test_file(ctx):
    """
    """
    node = ctx.path.find_or_declare('tests.py')

    if not os.path.exists(node.abspath()):
        return TestContainer({})

    return TestContainer(eval(node.read()[8:]))


def write_test_file(ctx, tests):
    node = ctx.path.find_or_declare('tests.py')

    node.write('tests = ' + repr(tests))



def get_tests(ctx):
    if hasattr(ctx, 'tests'):
        return ctx.tests

    ctx.tests = get_test_file(ctx)

    return ctx.tests


def get_sikuli_home(ctx):
    if sys.platform == 'darwin':
        return '/Applications/Sikuli-IDE.app/Contents/Resources/Java'

    raise NotImplementedError("Don't know how to determine default SIKULI_HOME")



def generate(src_node, dest_node, **context):
    """
    """
    from jinja2 import Template

    t = Template(src_node.read())

    dest_node.write(t.render(**context))



def generate_meerkat_lib(ctx, root, **context):
    """
    Builds a directory called `meerkat` at root_path and generates the
    ActionScript from within src/as/meerkat.
    """
    src_path = 'src/as/meerkat/'    
    meerkat_dir = root.find_or_declare('meerkat')

    for src in ctx.path.ant_glob(src_path + '*.as'):
        dest = meerkat_dir.find_or_declare(src.nice_path()[len(src_path):])
        generate(src, dest, **context)

    return meerkat_dir



def build_swf(ctx):
    """
    Build the meerkat AS library and then generate all suite SWFs.

    A SWF test is defined as under src directory that have the format swf/main.as
    """
    tests = get_tests(ctx)
    rule = '${MXMLC} -source-path=%s -output ${TGT} ${SRC}'

    swf_suite = ctx.path.find_or_declare('swf/suite')
    url = urlparse(ctx.env.SERVER_ROOT)

    for f in ctx.path.ant_glob('src/**/swf/main.as'):
        rel_path = f.abspath()[len(ctx.top_dir):].strip(os.path.sep)

        split_path = rel_path.split(os.path.sep)
        test_namespace = split_path[2:-2]

        c = tests.add('swf', '_'.join(test_namespace))

        p = swf_suite.find_or_declare(os.path.join(*test_namespace))
        lib = p.abspath()

        generate_meerkat_lib(ctx, p,
            server_url=url[0] + '://localhost:23456' + url[2] + '_'.join(test_namespace))

        # foo_bar_baz.swf
        swf_name = '_'.join(test_namespace) + '.swf'
        tgt = swf_suite.find_or_declare(swf_name)

        ctx(rule=rule % (lib,), source=f, target=tgt)

        c['file'] = tgt.bldpath()



def build_sikuli_runner(ctx):
    """
    Builds the Sikuli runner.
    """
    runner = ctx.path.find_or_declare('runner.sikuli')
    ctx.env.SIKULI_RUNNER = runner.nice_path()

    try:
        shutil.rmtree(runner.abspath())
    except OSError:
        pass

    shutil.copytree(ctx.path.find_node('src/runner.sikuli').abspath(), runner.abspath())



def build_runner(ctx):
    """
    Builds the Python test runner.
    """
    src = ctx.path.find_node('src/run.py')
    dest = ctx.path.find_or_declare('run.py')

    try:
        os.unlink(dest.abspath())
    except OSError:
        pass

    context = ctx.env.get_merged_dict().copy()

    context['LOCAL_SERVER'] = 'localhost:23456'
    context['REMOTE_SERVER'] = ctx.env.SERVER_ROOT

    generate(src, dest, **context)
    os.chmod(dest.abspath(), 0755)



def build_proxy(ctx):
    """
    Builds the Python test proxy.
    """
    src = ctx.path.find_node('src/proxy.py')
    dest = ctx.path.find_or_declare('proxy.py')

    try:
        os.unlink(dest.abspath())
    except OSError:
        pass

    generate(src, dest, **ctx.env.get_merged_dict())
    os.chmod(dest.abspath(), 0755)



def build_fms_apps(ctx):
    """
    Copies all src/test/suite/name/fms/* to build/fms/test_suite_name/*

    The contents in build/fms can then be dropped into an FMS install and restarted.
    """
    tests = get_tests(ctx)

    import shutil

    fms_build = ctx.path.find_or_declare('fms')

    for f in ctx.path.ant_glob('src/**/fms/main.asc'):
        app_src_dir = f.parent
        rel_path = f.abspath()[len(ctx.top_dir):].strip(os.path.sep)

        split_path = rel_path.split(os.path.sep)
        swf_namespace = split_path[2:-2]

        c = tests.add('fms', '_'.join(swf_namespace))

        app_node = fms_build.find_or_declare('_'.join(swf_namespace))

        try:
            shutil.rmtree(app_node.abspath())
        except OSError:
            pass

        shutil.copytree(app_src_dir.abspath(), app_node.abspath())
        c['app'] = app_node.nice_path()



def build_python_server_runner(ctx):
    """
    Copy the runner 
    """
    src = ctx.path.find_node('src/server_runner.py')
    dest = ctx.path.find_or_declare('python/runner.py')

    try:
        os.unlink(dest.abspath())
    except OSError:
        pass

    shutil.copy2(src.abspath(), dest.abspath())

    os.chmod(dest.abspath(), 0755)



def build_python_server(ctx):
    """
    Builds a number of python scripts that can be run from the commandline.
    """
    tests = get_tests(ctx)
    build_python_server_runner(ctx)

    server_build_node = ctx.path.find_or_declare('python/server')


    for f in ctx.path.ant_glob('src/**/python/server.py'):
        rel_path = f.abspath()[len(ctx.top_dir):].strip(os.path.sep)

        split_path = rel_path.split(os.path.sep)
        test_namespace = split_path[2:-2]
        module = '_'.join(test_namespace)
        c = tests.add('py_server', module)

        app_node = server_build_node.find_or_declare(module + '.py')

        try:
            os.unlink(app_node.abspath())
        except OSError:
            pass

        shutil.copy2(f.abspath(), app_node.abspath())
        c['file'] = app_node.nice_path()
        c['module'] = module



def deploy_fms_apps(ctx):
    """
    """
    tests = get_tests(ctx)
    rule = '${SCP} -r %s ${SCP_ARG}'

    fms_build = ctx.path.find_or_declare('fms')

    for name, context in tests.iteritems():
        app_dir = fms_build.find_or_declare(name).nice_path()

        ctx(rule=rule % app_dir)
