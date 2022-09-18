"""Recurring tasks used to organize the project.

http://www.pyinvoke.org/

"""

from pathlib import Path

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
    r = Path(f'test/data/{name}')
    r.mkdir()

    p = r / 'input/0.lissp'
    p.parent.mkdir()
    with p.open('w') as f:
        f.write('(lisscad.prelude.._macro_.standard)\n\n')
        f.write('(write ())\n')

    p = r / 'oracle/untitled_0_0.scad'
    p.parent.mkdir()
    p.write_text('')
