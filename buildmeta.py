"""
"""

import sys
import os.path
import shutil


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
    rule = '${MXMLC} -source-path=${MXMLC_LIB} -output ${TGT} ${SRC}'

    swf_suite = ctx.path.find_or_declare('swf/suite')

    for f in ctx.path.ant_glob('src/**/swf/main.as'):
        rel_path = f.abspath()[len(ctx.top_dir):].strip(os.path.sep)

        split_path = rel_path.split(os.path.sep)
        swf_namespace = split_path[2:-2]

        p = swf_suite.find_or_declare(os.path.join(*swf_namespace))
        ctx.env.MXMLC_LIB = p.abspath()

        generate_meerkat_lib(ctx, p,
            server_url=ctx.env.SERVER_ROOT + '_'.join(swf_namespace))

        # foo_bar_baz.swf
        swf_name = '_'.join(swf_namespace) + '.swf'
        tgt = swf_suite.find_or_declare(swf_name)

        ctx(rule=rule, source=f, target=tgt)



def build_runner(ctx):
    """
    Builds the Sikuli runner.
    """
    runner = ctx.path.find_or_declare('runner.sikuli')

    shutil.copytree(ctx.path.find_node('src/runner.sikuli').abspath(), runner.abspath())



def build_fms_apps(ctx):
    """
    Copies all src/test/suite/name/fms/* to build/fms/test_suite_name/*

    The contents in build/fms can then be dropped into an FMS install and restarted.
    """
    import shutil

    fms_build = ctx.path.find_or_declare('fms')

    for f in ctx.path.ant_glob('src/**/fms/main.asc'):
        app_src_dir = f.parent
        rel_path = f.abspath()[len(ctx.top_dir):].strip(os.path.sep)

        split_path = rel_path.split(os.path.sep)
        swf_namespace = split_path[2:-2]

        app_node = fms_build.find_or_declare('_'.join(swf_namespace))

        try:
            shutil.rmtree(app_node.abspath())
        except OSError:
            pass

        shutil.copytree(app_src_dir.abspath(), app_node.abspath())



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



def build_python_server(ctx):
    """
    Builds a number of python scripts that can be run from the commandline.

    These scripts
    """
    build_python_server_runner(ctx)

    server_build_node = ctx.path.find_or_declare('python/server')


    for f in ctx.path.ant_glob('src/**/python/server.py'):
        rel_path = f.abspath()[len(ctx.top_dir):].strip(os.path.sep)

        split_path = rel_path.split(os.path.sep)
        test_namespace = split_path[2:-2]

        app_node = server_build_node.find_or_declare('_'.join(test_namespace) + '.py')

        try:
            os.unlink(app_node.abspath())
        except OSError:
            pass

        shutil.copy2(f.abspath(), app_node.abspath())