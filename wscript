"""
"""

import buildmeta


top = '.'
out = 'build'


SERVER_TARGETS = ('py_server', 'fms')
CLIENT_TARGETS = ('swf', 'py_client')
PROTOCOLS = ('rtmp',)


def options(ctx):
    ctx.add_option('--server_targets', action='store',
        help=('A comma separated list of which server components to build (and '
            'test). Choose from %r' % (SERVER_TARGETS,)))
    ctx.add_option('--client_targets', action='store',
        help=('A comma separated list of which client components to build (and '
            'test). Choose from %r' % (CLIENT_TARGETS,)))

    ctx.add_option('--protocol', action='store', default='rtmp',
        help='Protocol to test. Choose ONE from %r.' % (PROTOCOLS,))

    for target in SERVER_TARGETS + CLIENT_TARGETS:
        ctx.load(target, tooldir='buildmeta')



def configure(ctx):
    target_server = ctx.options.server_targets

    if not target_server:
        ctx.fatal('--server_targets is a required argument.')

    target_server = target_server.split(',')
    targets = []

    for target in target_server:
        if target not in SERVER_TARGETS:
            ctx.fatal('Unknown server target %r.' % (target,))

        targets.append(target.strip())

    ctx.env.SERVER_TARGETS = targets

    client_targets = ctx.options.client_targets

    if not client_targets:
        ctx.fatal('--client_targets is a required argument.')

    client_targets = client_targets.split(',')
    targets = []

    for target in client_targets:
        if target not in CLIENT_TARGETS:
            ctx.fatal('Unknown client target %r.' % (target,))

        targets.append(target.strip())

    ctx.env.CLIENT_TARGETS = targets

    if not ctx.env.SERVER_TARGETS:
        ctx.fatal('At least one server target must be specified')

    if not ctx.env.CLIENT_TARGETS:
        ctx.fatal('At least one client target must be specified')

    protocol = ctx.options.protocol

    if not protocol:
        ctx.fatal('--protocol is a required argument.')

    if protocol not in PROTOCOLS:
        ctx.fatal('Unknown protocol %r.' % (protocol,))

    ctx.env.PROTOCOL = protocol

    for target in ctx.env.SERVER_TARGETS + ctx.env.CLIENT_TARGETS:
        ctx.load(target, tooldir='buildmeta')



def build(ctx):
    buildmeta.build_runner(ctx)
    buildmeta.build_proxy(ctx)

    buildmeta.clear_test_file(ctx)

    for target in ctx.env.SERVER_TARGETS + ctx.env.CLIENT_TARGETS:
        ctx.load(target, tooldir='buildmeta')

    buildmeta.write_test_file(ctx, buildmeta.get_tests(ctx))
