"""Recurring tasks used to organize the project.

http://www.pyinvoke.org/

"""

from pathlib import Path

from invoke import task


@task()
def snapshot_hissp(c, pipenv=False):
    """Install the latest development snapshot of Hissp.

    This was created before the release of Hissp v0.4.0, when lisscad
    was being designed for an unreleased new upstream API.

    """
    cmd = 'pip install -U git+https://github.com/gilch/hissp'
    if pipenv:
        cmd = 'pipenv run ' + cmd
    c.run(cmd)


@task()
def compile(c):
    """Compile bundled Lissp code to Python."""
    c.run('pipenv run python -c "'
          'from hissp import transpile; '
          'import lisscad; '
          r'transpile(lisscad.__package__, \"prelude\")'
          '"')


@task()
def typecheck(c):
    """Check data types."""
    c.run('pipenv run mypy .', pty=True)


@task(pre=[compile], default=True)
def test(c):
    """Run unit tests."""
    c.run('pipenv run pytest', pty=True)


@task(pre=[compile])
def build(c):
    """Build for distribution.

    The build process is based on setuptools controlled via the “build”
    package.

    """
    c.run('rm dist/*', warn=True)
    c.run('python -m build', pty=True)


@task(pre=[build])
def install(c):
    """Build a wheel and forcibly install it for empirical testing."""
    c.run('pip install --force-reinstall dist/*.whl')


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
