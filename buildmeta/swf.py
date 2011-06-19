"""
All code for options/configure/build for SWF target
"""

import sys
import os.path
import shutil


import buildmeta


def options(ctx):
    gr = ctx.add_option_group('Client target `swf`', 'Options for testing with '
        'standalone Flash Player')

    gr.add_option('--mxmlc', action='store', help='Path to mxmlc')
    gr.add_option('--flash_player', action='store',
        help='Full path to the standalone Flash Player')



def configure(ctx):
    """
    Configures meerkat to be able to build and test SWF clients.
    """
    mxmlc = ctx.options.mxmlc

    if not mxmlc:
        mxmlc = ctx.find_program('mxmlc')

    ctx.env.MXMLC = os.path.abspath(os.path.expanduser(mxmlc))

    ctx.env.JAVA = ctx.find_program('java')

    if not ctx.env.SIKULI_HOME:
        ctx.env.SIKULI_HOME = get_sikuli_home(ctx)
        ctx.msg('Setting SIKULI_HOME', ctx.env.SIKULI_HOME)

    if not os.path.exists(ctx.env.SIKULI_HOME):
        ctx.fatal('Unable to find Sikuli at %r' % (ctx.env.SIKULI_HOME,))

    ctx.env.FLASH_PLAYER = ctx.options.flash_player

    if not ctx.env.FLASH_PLAYER:
        ctx.fatal('Standalone Flash player required, supply --flash_player')

    ctx.msg('Using Flash Standalone Player', ctx.env.FLASH_PLAYER)



def build(ctx):
    build_swf(ctx)
    build_sikuli_runner(ctx)



def get_sikuli_home(ctx):
    if sys.platform == 'darwin':
        return '/Applications/Sikuli-IDE.app/Contents/Resources/Java'

    raise NotImplementedError("Don't know how to determine default SIKULI_HOME")



def generate_meerkat_lib(ctx, root, **context):
    """
    Builds a directory called `meerkat` at root_path and generates the
    ActionScript from within src/as/meerkat.
    """
    src_path = 'src/as/meerkat/'
    meerkat_dir = root.find_or_declare('meerkat')

    for src in ctx.path.ant_glob(src_path + '*.as'):
        dest = meerkat_dir.find_or_declare(src.nice_path()[len(src_path):])
        buildmeta.generate(src, dest, **context)

    return meerkat_dir



def build_swf(ctx):
    """
    Build the meerkat AS library and then generate all suite SWFs.

    A SWF test is defined as under src directory that have the format swf/main.as
    """
    tests = buildmeta.get_tests(ctx)
    rule = '${MXMLC} -source-path=%s -output ${TGT} ${SRC}'

    swf_suite = ctx.path.find_or_declare('swf/suite')

    for f in ctx.path.ant_glob('src/**/swf/main.as'):
        rel_path = f.srcpath()

        split_namespace = rel_path.split(os.path.sep)[2:-2]
        namespace = '_'.join(split_namespace)

        c = tests.add('swf', namespace)

        p = swf_suite.find_or_declare(os.path.join(*split_namespace))

        generate_meerkat_lib(ctx, p,
            server_url=ctx.env.PROTOCOL + '://localhost:23456/' + namespace)

        tgt = swf_suite.find_or_declare(namespace + '.swf')

        ctx(rule=rule % (p.abspath(),), source=f, target=tgt)

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
