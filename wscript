"""
"""

import sys
import os.path


top = '.'
out = 'build'


def options(ctx):
    ctx.add_option('--mxmlc', action='store', help='Path to mxmlc')
    ctx.add_option('--server_root', action='store', help='Server URL to connect to when running the suite. e.g. rtmp://10.1.1.5/. The path of the url is set automatically at build time.')
    ctx.add_option('--logging', action='store', default='', help='Logging URL to use when sending logging info')



def configure(ctx):
    mxmlc = ctx.options.mxmlc

    if not mxmlc:
        mxmlc = ctx.find_program('mxmlc')

    ctx.env.MXMLC = os.path.abspath(os.path.expanduser(mxmlc))
    ctx.env.SERVER_ROOT = ctx.options.server_root.rstrip('/') + '/'
    ctx.env.JAVA = ctx.find_program('java')

    if not ctx.env.SIKULI_HOME:
        ctx.env.SIKULI_HOME = get_sikuli_home(ctx)
        ctx.msg('Setting SIKULI_HOME', ctx.env.SIKULI_HOME)

    if not os.path.exists(ctx.env.SIKULI_HOME):
        ctx.fatal('Unable to find Sikuli at %r' % (ctx.env.SIKULI_HOME,))



def get_sikuli_home(ctx):
    if sys.platform == 'darwin':
        return '/Applications/Sikuli-IDE.app/Contents/Resources/Java'

    raise NotImplementedError("Don't know how to determine default SIKULI_HOME")



def generate_meerkat_file(ctx, src_node, dest_node, **context):
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
        generate_meerkat_file(ctx, src, dest, **context)

    return meerkat_dir



def build_swf(ctx):
    """Build the meerkat AS library and then generate all suite SWFs.

    A SWF test is defined as under src directory that have the format swf/main.as
    """
    swf_lib = ctx.path.find_or_declare('swf/lib')
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


def build(ctx):
    build_swf(ctx)
