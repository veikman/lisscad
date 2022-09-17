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


@task(pre=[compile])
def test(c):
    """Run unit tests."""
    c.run('pytest')
