"""Custom exceptions for the lisscad package."""


class LisscadError(Exception):
    """Root exception class for the lisscad package."""


class Failure(LisscadError):
    """A failure in transpilation or rendering."""

    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.description = kwargs
