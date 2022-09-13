"""Automated integration testing using lissp subprocesses."""

from pathlib import Path
from unittest.mock import patch

from hissp.reader import Lissp
from lisscad.app import _compose_scad_output_path
from pytest import fail, mark, skip

CASES = sorted(Path('test/data/').glob('*'))


@mark.parametrize('case', CASES)
def test_lissp_to_scad(case, tmp_path, pytestconfig):
    """Compare a prepared set of files with outputs from them.

    If the custom “adopt” option has been passed to pytest, replace oracles
    with real outputs from the system under test, assuming correctness.

    """
    dir_in = case / 'input'
    dir_oracle = case / 'oracle'

    assert dir_in.is_dir()
    assert dir_oracle.is_dir()

    files_input = sorted(dir_in.glob('*.lissp'))
    if not files_input:
        fail(f'No input for “{case}”.')

    files_oracle = list(dir_oracle.glob('**/*.*'))
    if not files_oracle:
        fail(f'No oracle for “{case}”.')

    with patch(
            'lisscad.app._compose_scad_output_path',
            new=lambda _, asset: _compose_scad_output_path(tmp_path, asset)):
        for file_in in files_input:
            code = file_in.read_text()
            try:
                Lissp(evaluate=True).compile(code)
            except Exception as e:
                fail(f'Lissp compiler error: {e!r}')

    for stored_oracle in files_oracle:
        file_out = tmp_path / (stored_oracle.relative_to(dir_oracle))
        content_out = file_out.read_text().rstrip()
        content_oracle = stored_oracle.read_text().rstrip()

        try:
            assert content_out == content_oracle
        except AssertionError:
            if pytestconfig.getoption('adopt'):
                stored_oracle.write_text(content_out + '\n')
                skip('New output adopted.')
            raise
