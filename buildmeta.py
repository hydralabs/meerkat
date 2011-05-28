"""
"""

import sys
import os.path


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
