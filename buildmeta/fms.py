"""
All code for options/configure/build for FMS target
"""

import os.path

import buildmeta



def options(ctx):
    gr = ctx.add_option_group('Server target `fms`', 'Options for testing against '
        'Flash Media Server')

    gr.add_option('--fms_user', action='store',
        help='Username used by SCP to connect to FMS host server')
    gr.add_option('--fms_passwd', action='store',
        help='Password used by FMS Admin too to reload the vhost for this test run')
    gr.add_option('--fms_host', action='store',
        help='Host used by SCP to connect to FMS host server')
    gr.add_option('--fms_dir', action='store',
        help='Absolute path to the applications directory for that')



def configure(ctx):
    """
    Configures meerkat to be able to build and test against an FMS server.
    """
    fms_user = ctx.options.fms_user

    if not fms_user:
        ctx.fatal('FMS User required, supply --fms_user')

    fms_host = ctx.options.fms_host

    if not fms_host:
        ctx.fatal('FMS Host required, supply --fms_host')

    fms_dir = ctx.options.fms_dir.rstrip('/')

    if not fms_dir:
        ctx.fatal('FMS application directory required, supply --fms_dir')

    fms_passwd = ctx.options.fms_passwd

    if not fms_passwd:
        ctx.fatal('FMS Passwd required, supply --fms_passwd')

    ctx.env.SCP = ctx.find_program('scp')
    ctx.env.SSH = ctx.find_program('ssh')

    scp_arg = '%s@%s:%s' % (fms_user, fms_host, fms_dir)

    ctx.msg('Will deploy FMS apps to', scp_arg)

    ctx.env.FMS_USER = fms_user
    ctx.env.FMS_PASSWD = fms_passwd
    ctx.env.FMS_HOST = fms_host
    ctx.env.FMS_DIR = fms_dir

    ctx.msg('Setting FMS_USER', ctx.env.FMS_USER)
    ctx.msg('Setting FMS_PASSWD', ctx.env.FMS_PASSWD)
    ctx.msg('Setting FMS_HOST', ctx.env.FMS_HOST)
    ctx.msg('Setting FMS_DIR', ctx.env.FMS_DIR)

    assert ctx.env.FMS_DIR.startswith('/opt/adobe/fms')



def build(ctx):
    """
    """
    build_apps(ctx)
    deploy_fms_apps(ctx)



def build_apps(ctx):
    """
    Copies all src/test/suite/name/fms/* to build/fms/test_suite_name/*

    The contents in build/fms can then be dropped into an FMS install and
    restarted.
    """
    tests = buildmeta.get_tests(ctx)

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
        c['app_name'] = '_'.join(swf_namespace)



def deploy_fms_apps(ctx):
    """
    """
    tests = buildmeta.get_tests(ctx)
    context = ctx.env.get_merged_dict().copy()

    fms_deploy = ctx.path.find_or_declare('fms-deploy')
    fms_build = ctx.path.find_or_declare('fms')

    lines = []

    for name in tests:
        app_dir = fms_build.find_or_declare(name)
        c = context.copy()
        c.update({'APP_NAME': name, 'APP_DIR': app_dir.abspath()})

        lines.append('%(SSH)s %(FMS_USER)s@%(FMS_HOST)s "rm -rf %(FMS_DIR)s/%(APP_NAME)s"' % c)
        lines.append('%(SCP)s -r %(APP_DIR)s %(FMS_USER)s@%(FMS_HOST)s:%(FMS_DIR)s' % c)

    fms_deploy.write('\n'.join(lines) + '\n', 'w+')
    os.chmod(fms_deploy.abspath(), 0755)
