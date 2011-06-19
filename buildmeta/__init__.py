"""
"""

import os.path



class TestContainer(dict):
    """
    """

    def __init__(self, d):
        self.update(d)

    def add(self, type, name):
        return self.setdefault(name, {}).setdefault(type, {})



def clear_test_file(ctx):
    """
    """
    n = ctx.path.find_or_declare('tests.py')

    n.delete()



def get_test_file(ctx):
    """
    """
    node = ctx.path.find_or_declare('tests.py')

    if not os.path.exists(node.abspath()):
        return TestContainer({})

    return TestContainer(eval(node.read()[8:]))



def write_test_file(ctx, tests):
    node = ctx.path.find_or_declare('tests.py')

    node.write('tests = ' + repr(tests))



def get_tests(ctx):
    if hasattr(ctx, 'tests'):
        return ctx.tests

    ctx.tests = get_test_file(ctx)

    return ctx.tests



def generate(src_node, dest_node, **context):
    """
    """
    from jinja2 import Template

    t = Template(src_node.read())

    dest_node.write(t.render(**context))



def build_runner(ctx):
    """
    Builds the Python test runner.
    """
    src = ctx.path.find_node('src/run.py')
    dest = ctx.path.find_or_declare('run.py')

    try:
        os.unlink(dest.abspath())
    except OSError:
        pass

    context = ctx.env.get_merged_dict().copy()

    context['LOCAL_SERVER'] = 'localhost:23456'

    generate(src, dest, **context)
    os.chmod(dest.abspath(), 0755)



def build_proxy(ctx):
    """
    Builds the Python test proxy.
    """
    src = ctx.path.find_node('src/proxy.py')
    dest = ctx.path.find_or_declare('proxy.py')

    try:
        os.unlink(dest.abspath())
    except OSError:
        pass

    generate(src, dest, **ctx.env.get_merged_dict())
    os.chmod(dest.abspath(), 0755)
