"""
"""

import os.path

import buildmeta


top = '.'
out = 'build'


def options(ctx):
    ctx.add_option('--mxmlc', action='store', help='Path to mxmlc')
    ctx.add_option('--server_root', action='store', help='Server URL to connect to when running the suite. e.g. rtmp://10.1.1.5/. The path of the url is set automatically at build time.')
    ctx.add_option('--logging', action='store', default='', help='Logging URL to use when sending logging info')
    ctx.add_option('--flash_player', action='store', default='', help='Full path to the Standalone Flash Player')



def configure(ctx):
    mxmlc = ctx.options.mxmlc

    if not mxmlc:
        mxmlc = ctx.find_program('mxmlc')

    ctx.env.MXMLC = os.path.abspath(os.path.expanduser(mxmlc))

    if not ctx.options.server_root:
        ctx.fatal('Require --server_root arg')

    ctx.env.SERVER_ROOT = ctx.options.server_root.rstrip('/') + '/'
    ctx.env.JAVA = ctx.find_program('java')

    if not ctx.env.SIKULI_HOME:
        ctx.env.SIKULI_HOME = buildmeta.get_sikuli_home(ctx)
        ctx.msg('Setting SIKULI_HOME', ctx.env.SIKULI_HOME)

    if not os.path.exists(ctx.env.SIKULI_HOME):
        ctx.fatal('Unable to find Sikuli at %r' % (ctx.env.SIKULI_HOME,))

    ctx.env.FLASH_PLAYER = ctx.options.flash_player

    if not ctx.env.FLASH_PLAYER:
        ctx.fatal('Standalone Flash player required, supply --flash_player')

    ctx.msg('Using Flash Standalone Player', ctx.env.FLASH_PLAYER)



def build(ctx):
    buildmeta.build_swf(ctx)
    #buildmeta.build_runner(ctx)
    buildmeta.build_fms_apps(ctx)


def run(ctx):
    """
    Run the test suite.

    Ensures that the server component is deployed and iterates over all the swfs
    using Sikuli to determine a result for that test.
    """
