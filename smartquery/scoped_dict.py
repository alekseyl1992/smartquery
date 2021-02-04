from contextlib import contextmanager


class ScopedDict:
    def __init__(self, initial_scope: dict):
        self.scopes = [initial_scope]

    def push_scope(self, scope: dict):
        self.scopes.append(scope)

    def pop_scope(self):
        self.scopes.pop()

    def __getitem__(self, item):
        for scope in reversed(self.scopes):
            if item in scope:
                return scope[item]

        raise KeyError(str(item))

    def __setitem__(self, key, value):
        self.scopes[-1][key] = value

    @contextmanager
    def make_scope(self, scope: dict):
        self.push_scope(scope)
        try:
            yield self
        finally:
            self.pop_scope()
