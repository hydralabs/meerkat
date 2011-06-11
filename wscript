"""
"""

import os.path

import buildmeta


top = '.'
out = 'build'


SERVER_TYPES = ['py_server', 'fms']
CLIENT_TYPES = ['swf']


def options(ctx):
    ctx.add_option('--mxmlc', action='store', help='Path to mxmlc')
    ctx.add_option('--target_server', action='store', help='The target server type to test. Choose from %r' % (SERVER_TYPES,))
    ctx.add_option('--target_client', action='store', help='The target client type to test. Choose from %r' % (CLIENT_TYPES,))
    ctx.add_option('--server_root', action='store', help='Server URL to connect to when running the suite. e.g. rtmp://10.1.1.5/. The path of the url is set automatically at build time.')
    ctx.add_option('--logging', action='store', default='', help='Logging URL to use when sending logging info')
    ctx.add_option('--flash_player', action='store', default='', help='Full path to the Standalone Flash Player')
    ctx.add_option('--scp_arg', action='store', help='scp username@host:/root arg used to deploy FMS apps (used only if target_server=="fms"')



def configure(ctx):
    target_server = ctx.options.target_server

    if not target_server:
        ctx.fatal('--target_server is a required argument. Choose from %r' % (SERVER_TYPES,))

    if target_server not in SERVER_TYPES:
        ctx.fatal('Unknown server type %r, choose from %r' % (target_server, SERVER_TYPES))

    ctx.env.TARGET_SERVER = target_server

    target_client = ctx.options.target_client

    if not target_client:
        ctx.fatal('--target_client is a required argument. Choose from %r' % (CLIENT_TYPES,))

    if target_client not in CLIENT_TYPES:
        ctx.fatal('Unknown client type %r, choose from %r' % (target_client, CLIENT_TYPES))

    ctx.env.TARGET_CLIENT = target_client

    if target_client == 'swf':
        mxmlc = ctx.options.mxmlc

        if not mxmlc:
            mxmlc = ctx.find_program('mxmlc')

        ctx.env.MXMLC = os.path.abspath(os.path.expanduser(mxmlc))

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

    if not ctx.options.server_root:
        ctx.fatal('Require --server_root arg')

    ctx.env.SERVER_ROOT = ctx.options.server_root.rstrip('/') + '/'

    if target_server == 'fms':
        ctx.env.SCP = ctx.find_program('scp')

        scp_arg = ctx.options.scp_arg

        if not scp_arg:
            ctx.fatal('FMS SCP arg required for app deployment, supply --scp_arg')

        ctx.msg('Will deploy FMS apps to', scp_arg)

        ctx.env.SCP_ARG = scp_arg


        

def build(ctx):
    target_server = ctx.env.TARGET_SERVER
    target_client = ctx.env.TARGET_CLIENT

    buildmeta.clear_test_file(ctx)

    if target_client == 'swf':
        buildmeta.build_swf(ctx)
        buildmeta.build_sikuli_runner(ctx)

    if target_server == 'fms':
        buildmeta.build_fms_apps(ctx)
        buildmeta.deploy_fms_apps(ctx)
    elif target_server == 'py_server':
        buildmeta.build_python_server(ctx)

    buildmeta.build_runner(ctx)
    buildmeta.build_proxy(ctx)

    buildmeta.write_test_file(ctx, buildmeta.get_tests(ctx))
