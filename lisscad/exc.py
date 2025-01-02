"""Custom exceptions for the lisscad package."""


class LisscadError(Exception):
    """Root exception class for the lisscad package."""


class Failure(LisscadError):
    """A failure in transpilation or rendering."""

    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.description = kwargs


class OperatorError(LisscadError):
    """An invalid use of an operator like “+”."""


class DimensionalityError(LisscadError):
    """An invalid dimensionality."""


class DimensionalityZeroError(DimensionalityError):
    """An invalid zero-dimensional geometry."""


class DimensionalityMismatchError(DimensionalityError):
    """An invalid combination of 2D and 3D."""
