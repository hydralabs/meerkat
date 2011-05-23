"""
"""

import os.path


top = '.'
out = 'build'


def options(ctx):
    ctx.add_option('--mxmlc', action='store', help='Path to mxmlc')



def configure(ctx):
    mxmlc = ctx.options.mxmlc

    if not mxmlc:
        mxmlc = ctx.find_program('mxmlc')

    ctx.env.MXMLC = os.path.abspath(os.path.expanduser(mxmlc))



def build_swf(ctx):
    """
    Find all files that have the main.as
    """
    ctx.env.MXMLC_LIB = ctx.path.find_node('lib').abspath()
    rule = '${MXMLC} -source-path=${MXMLC_LIB} -output ${TGT} ${SRC}'

    for f in ctx.path.ant_glob('src/**/swf/main.as'):
        rel_path = f.abspath()[len(ctx.top_dir):].strip(os.path.sep)

        # foo_bar_baz.swf
        tgt = 'swf/' + '_'.join(rel_path.split(os.path.sep)[1:-2]) + '.swf'
        ctx.path.find_or_declare(tgt)

        ctx(rule=rule, source=f, target=tgt)


def build(ctx):
    build_swf(ctx)
