"""Recurring tasks used to organize the project.

http://www.pyinvoke.org/

"""

from pathlib import Path

from invoke import task


@task()
def snapshot_hissp(c):
    """Install the latest development snapshot of Hissp."""
    c.run('pipenv run '
          'pip install -U git+https://github.com/gilch/hissp')


@task()
def compile(c):
    """Compile bundled Lissp code to Python."""
    c.run('pipenv run python -c "'
          'from hissp import transpile; '
          'import lisscad; '
          r'transpile(lisscad.__package__, \"prelude\")'
          '"')


@task(pre=[compile], default=True)
def test(c):
    """Run unit tests."""
    c.run('pipenv run pytest', pty=True)


@task()
def build(c):
    """Build for distribution.

    The build process is based on setuptools controlled via the “build”
    package.

    """
    c.run('python -m build')


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
