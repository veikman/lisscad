"""Custom exceptions for the lisscad package."""


class Failure(Exception):
    """A failure in transpilation or rendering."""

    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.description = kwargs
