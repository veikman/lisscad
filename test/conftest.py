"""Customization of pytest."""


def pytest_addoption(parser):
    parser.addoption(
        "--adopt",
        default=False,
        action="store_true",
        help="Take test output files as correct",
    )
    parser.addoption(
        "--render",
        default=False,
        action="store_true",
        help="Run OpenSCAD to render generated code as an extra check",
    )
