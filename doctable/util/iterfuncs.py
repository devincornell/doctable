
import typing


T = typing.TypeVar('T')


def ungroupby(groups: typing.Dict[typing.Hashable, T]):
    '''Flatten any list'''
    pass

def groupby(
        elements: typing.Iterable[T], 
        keys: typing.List[typing.Callable[[T], typing.Hashable]],
    ) -> typing.Dict[typing.Hashable, typing.Dict[typing.Hashable, typing.List[T]]]:
    '''Groups elements of the list into nested dictionaries according to group funcs.'''
    
    groups = dict()
    num_keys = len(keys)
    for el in elements:
        # down each level of the heirarchy
        grp = groups
        for i, key_func in enumerate(keys):
            k = key_func(el)
            if i < (num_keys - 1):
                grp.setdefault(k, dict())
                grp = grp[k]
            else:
                grp.setdefault(k, list())
                grp[k].append(el)
    return groups
        

