"""Recurring tasks used to organize the project.

http://www.pyinvoke.org/

"""

from invoke import task


@task()
def compile(c):
    """Compile bundled Lissp code to Python."""
    c.run('python -c "'
          'from hissp import transpile; '
          'import lisscad; '
          r'transpile(lisscad.__package__, \"prelude\")'
          '"')


@task(pre=[compile], default=True)
def test(c):
    """Run unit tests."""
    c.run('pytest', pty=True)


@task
def new_case(c, name):
    """Add a new integration test case."""
    c.run(f'mkdir -p test/data/{name}/input')
    c.run(f'mkdir test/data/{name}/oracle')
