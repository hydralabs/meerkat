"""
"""

import buildmeta


top = '.'
out = 'build'


SERVER_TARGETS = ('py_server', 'fms')
CLIENT_TARGETS = ('swf', 'py_client')
# supported protocols
PROTOCOLS = ('rtmp',)
AMF_VERSIONS = ('0', 3)


def options(ctx):
    ctx.add_option('--server', action='store',
        help='A server component to build (and test). Choose one from %r' % (
            SERVER_TARGETS,))

    ctx.add_option('--client', action='store',
        help='A client component to build (and test). Choose one from %r' % (
            CLIENT_TARGETS,))

    ctx.add_option('--protocol', action='store', default='rtmp',
        help='Protocol to test. Choose ONE from %r.' % (PROTOCOLS,))

    ctx.add_option('--remote_host', action='store', help='The hostname that '
        'will be used by the client target to connect to the server target')

    ctx.add_option('--amf_encoding', action='store', help='The AMF version used '
        'to connect to the server target', default='0')

    for target in SERVER_TARGETS + CLIENT_TARGETS:
        ctx.load(target, tooldir='buildmeta')



def configure(ctx):
    server_target = ctx.options.server

    if not server_target:
        ctx.fatal('--server is a required argument.')

    if server_target not in SERVER_TARGETS:
        ctx.fatal('Unknown server target %r.' % (server_target,))

    ctx.env.SERVER_TARGET = server_target


    client_target = ctx.options.client

    if not client_target:
        ctx.fatal('--client is a required argument.')

    if client_target not in CLIENT_TARGETS:
        ctx.fatal('Unknown client target %r.' % (client_target,))

    ctx.env.CLIENT_TARGET = client_target


    protocol = ctx.options.protocol

    if not protocol:
        ctx.fatal('--protocol is a required argument.')

    if protocol not in PROTOCOLS:
        ctx.fatal('Unknown protocol %r.' % (protocol,))

    ctx.env.PROTOCOL = protocol


    amf_encoding = ctx.options.amf_encoding

    if not amf_encoding:
        ctx.fatal('--amf_encoding is a required argument.')

    if amf_encoding not in AMF_VERSIONS:
        ctx.fatal('Unknown AMF encoding %r.' % (amf_encoding,))


    remote_host = ctx.options.remote_host

    if not remote_host:
        ctx.fatal('--remote_host is a required argument.')


    # parse remote_host for host:port
    host = remote_host
    port = '1935'
    res = remote_host.split(':')

    if res[0] != remote_host:
        host, port = res

    ctx.env.REMOTE_SERVER = host + ':' + port
    ctx.msg('Setting REMOTE_SERVER', ctx.env.REMOTE_SERVER)

    ctx.load('python')
    ctx.check_python_module('jinja2')

    for target in [ctx.env.SERVER_TARGET, ctx.env.CLIENT_TARGET]:
        ctx.load(target, tooldir='buildmeta')



def build(ctx):
    buildmeta.build_runner(ctx)
    buildmeta.build_proxy(ctx)

    buildmeta.clear_test_file(ctx)

    for target in [ctx.env.SERVER_TARGET, ctx.env.CLIENT_TARGET]:
        ctx.load(target, tooldir='buildmeta')

    buildmeta.write_test_file(ctx, buildmeta.get_tests(ctx))
