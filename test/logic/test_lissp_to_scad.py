"""Automated integration testing using lissp subprocesses."""

from itertools import count
from pathlib import Path
from unittest.mock import patch

from hissp.reader import Lissp
from pytest import fail, mark, skip

from lisscad.app import _compose_scad_output_path

CASES = [(p.name, p) for p in sorted(Path('test/data/').glob('*'))]


@mark.parametrize('_, case', CASES)
def test_lissp_to_scad(_, case, tmp_path, pytestconfig):
    """Compare a prepared set of files with outputs from them.

    If the custom “adopt” option has been passed to pytest, replace oracles
    with real outputs from the system under test, assuming correctness.

    """
    dir_in = case / 'input'
    print(dir_in)
    dir_oracle = case / 'oracle'

    if not dir_in.is_dir():
        fail(f'No input directory at {dir_in}.')
    if not dir_oracle.is_dir():
        fail(f'No reference directory at {dir_in}.')

    files_input = sorted(dir_in.glob('*.lissp'))
    if not files_input:
        fail(f'No files in {dir_in}.')

    files_oracle = list(dir_oracle.glob('**/*.*'))
    if not files_oracle:
        fail(f'No files in {dir_oracle}.')

    with patch(
            'lisscad.app._compose_scad_output_path',
            new=lambda _, asset: _compose_scad_output_path(tmp_path, asset)):
        for file_in in files_input:
            code = file_in.read_text()
            try:
                # Reset _INVOCATION_ORDINAL as if in a new process.
                with patch('lisscad.app._INVOCATION_ORDINAL', new=count()):
                    Lissp(evaluate=True).compile(code)
            except Exception as e:
                fail(f'Lissp compiler error: {e!r}')

    adopted = False
    for stored_oracle in files_oracle:
        file_out = tmp_path / (stored_oracle.relative_to(dir_oracle))
        content_out = file_out.read_text().rstrip()
        content_oracle = stored_oracle.read_text().rstrip()

        try:
            assert content_out == content_oracle
        except AssertionError:
            if pytestconfig.getoption('adopt'):
                stored_oracle.write_text(content_out + '\n')
                adopted = True
                continue
            raise
    if adopted:
        skip('New output adopted.')
