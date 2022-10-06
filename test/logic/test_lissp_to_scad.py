"""Automated integration testing using lissp subprocesses."""

from ast import literal_eval
from functools import partial
from itertools import count
from pathlib import Path
from unittest.mock import Mock, patch

from hissp.reader import Lissp
from pytest import fail, mark, skip

from lisscad.app import _compose_scad_output_path, _process_all, write

CASES = [(p.name, p) for p in sorted(Path('test/data/').glob('*'))]

FILE_RENDERCALLS = 'rendercalls.py'


@mark.parametrize('_, case', CASES)
def test_lissp_to_scad(_, case, tmp_path, pytestconfig):
    """Compare a prepared set of files with outputs from them.

    If the custom “adopt” option has been passed to pytest, replace oracles
    with real outputs from the system under test, assuming correctness.

    """
    adopt = pytestconfig.getoption('adopt')

    dir_in = case / 'input'
    dir_oracle = case / 'oracle'

    if not dir_in.is_dir():
        fail(f'No input directory at {dir_in}.')

    if adopt:
        dir_oracle.mkdir(exist_ok=True)

    if not dir_oracle.is_dir():
        fail(f'No reference directory at {dir_in}.')

    files_input = sorted(dir_in.glob('*.lissp'))
    if not files_input:
        fail(f'No files in {dir_in}.')

    files_oracle = list(dir_oracle.glob('**/*.*'))
    if not files_oracle and not adopt:
        fail(f'No files in {dir_oracle}.')

    def mock_fork(scadjobs, renderjobs, report_progress, report_failure):
        """Skip the forking."""
        _process_all(Mock(), scadjobs, renderjobs)
        assert callable(report_progress)
        assert callable(report_failure)

    runs = []

    def _replace_tmp(cmd: list[str]) -> list[str]:
        """Paper over the uniqueness of tmp_path."""
        return [c.replace(str(tmp_path), 'fixture') for c in cmd]

    def mock_render_all(_, renderjobs):
        """Skip the process pool."""
        for _, __, cmd in renderjobs:
            runs.append(_replace_tmp(cmd))

    with (
            # Place files in /tmp.
            patch('lisscad.app._compose_scad_output_path',
                  new=lambda _, asset: _compose_scad_output_path(
                      tmp_path, asset)),
            # Don’t create processes or wait for their reports.
            patch('lisscad.app._fork', new=mock_fork),
            patch('lisscad.app._render_all', new=mock_render_all),
            # Unlike the lissp CLI, pytest leaves sys.argv intact after parsing
            # its own arguments. An empty vector is passed to write here via
            # patch, so that write’s internal CLI parser does not exit with an
            # error when pytest is called with an argument.
            patch('lisscad.app.write', new=partial(write, argv=[]))):
        for file_in in files_input:
            code = file_in.read_text()
            try:
                # Reset _INVOCATION_ORDINAL as if in a new process.
                with patch('lisscad.app._INVOCATION_ORDINAL', new=count()):
                    Lissp(evaluate=True).compile(code)
            except Exception as e:
                fail(f'Lissp compiler error: {e!r}')

    adopted = _check_processes(adopt, case / FILE_RENDERCALLS, runs)

    for file_out in sorted(tmp_path.glob('*.scad')):
        matching_oracle = dir_oracle / file_out.name
        if not matching_oracle.is_file():
            if adopt:
                matching_oracle.write_text(file_out.read_text())
                adopted = True
                continue
            fail(f'No oracle for output {file_out.name}.')

    for stored_oracle in files_oracle:
        file_out = tmp_path / stored_oracle.relative_to(dir_oracle)
        content_out = file_out.read_text().rstrip()
        content_oracle = stored_oracle.read_text().rstrip()

        try:
            assert content_oracle == content_out
        except AssertionError:
            if adopt:
                stored_oracle.write_text(content_out + '\n')
                adopted = True
                continue
            raise

    if adopted:
        skip('New output adopted.')


class _MockProcess(Mock):
    """Imitate the interface of multiprocessing.Process."""

    def __init__(self, target, args):
        super().__init__()
        target(*args)  # Call target in calling thread.

    def start(self):
        pass

    def join(self):
        pass


def _check_processes(adopt: bool, file: Path, calls: list[tuple[str,
                                                                ...]]) -> bool:
    if file.exists():
        oracle = literal_eval(file.read_text())
        try:
            assert calls == oracle
        except AssertionError:
            if calls and adopt:
                file.write_text(str(calls))
                return True
            raise
        else:
            return False

    # Else file does not exist.
    if calls:
        if calls and adopt:
            file.write_text(str(calls))
            return True

        fail('Called to render.')

    # No oracle, no calls.
    return False
