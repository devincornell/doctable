import typing


def assert_set_len_eq(x: typing.Any, y: typing.Any) -> None:
    f = lambda x: len(set(x))
    try:
        assert(f(x)) == f(y)
    except AssertionError as e:
        raise AssertionError(f'Failed: {len(set(x))=} != {len(set(y))=}. '
        f'The sets were different sizes.')

def assert_set_eq(x: typing.Any, y: typing.Any) -> None:
    try:
        assert(set(x)) == set(y)
    except AssertionError as e:
        raise AssertionError(f'Failed: set({len(set(x))=}) != set({len(set(y))=})')

def assert_eq(x: typing.Any, y: typing.Any) -> None:
    try:
        assert(x == y)
    except AssertionError as e:
        raise AssertionError(f'Failed: x != y:\n{x=}\n{y=}')
    
