import typing

T = typing.TypeVar('T')

def assert_set_len_eq(x: T, y: T) -> None:
    f = lambda x: len(set(x))
    if f(x) == f(y):
        raise AssertionError(f'Failed assertion: {len(set(x))=} != {len(set(y))=}. '
        f'The sets were different sizes.')

def assert_set_eq(x: T, y: T) -> None:
    if set(x) != set(y):
        raise AssertionError(f'Failed assertion: set({len(set(x))=}) != set({len(set(y))=})')

def assert_eq(x: T, y: T) -> None:
    if x != y:
        raise AssertionError(f'Failed assertion x == y:\n{x=}\n{y=}')

def assert_neq(x: T, y: T) -> None:
    if x == y:
        raise AssertionError(f'Failed assertion x != y:\n{x=}\n{y=}')

def assert_ge(x: T, y: T) -> None:
    if x < y:
        raise AssertionError(f'Failed assertion x >= y:\n{x=}\n{y=}')

def assert_gt(x: T, y: T) -> None:
    if x <= y:
        raise AssertionError(f'Failed assertion: x > y:\n{x=}\n{y=}')

def assert_eq_transform(x: T, y: T, f: typing.Callable[[T],typing.Any]):
    if f(x) != f(y):
        raise AssertionError(f'Failed assertion: {f(x)=} != f({f(y)=}).')
