"""memory/exceptions.py"""

"""
memory/exceptions.py


"""

class MemoryError(Exception):
    pass


class RepositoryError(MemoryError):
    pass


class ValidationError(MemoryError):
    pass


class RetrievalError(MemoryError):
    pass