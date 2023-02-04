from __future__ import annotations

import typing


T = typing.TypeVar('T')


class GroupedData(typing.Dict[typing.Hashable, typing.Union[typing.List, typing.Dict]]):
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'
    
    ################### Grouping ###################
    @classmethod
    def group_elements(cls, 
            elements: typing.Iterable[T], 
            keys: typing.List[typing.Callable[[T], typing.Hashable]],
        ) -> GroupedData:
        '''Groups elements of the list into nested dictionaries according to group funcs.'''
        
        groups = cls()
        num_keys = len(keys)
        for el in elements:
            # down each level of the heirarchy
            grp = groups
            for i, key_func in enumerate(keys):
                k = key_func(el)
                if i < (num_keys - 1):
                    grp.setdefault(k, cls())
                    grp = grp[k]
                else:
                    grp.setdefault(k, list())
                    grp[k].append(el)
        return groups
    
    ################### Flattening ###################
    def ungroup(self) -> typing.List[typing.Tuple[typing.Tuple[typing.Hashable], T]]:
        elements = list()
        for keys, els in self.flatten().items():
            for e in els:
                elements.append((keys, e))
        return elements
    
    
    def flatten(self) -> GroupedData:
        groups = self.__class__()
        for k,els in self.items():
            if hasattr(els, 'flatten'):
                for ks, e in els.flatten().items():
                    groups[(k,)+ks] = e
            else:
                groups[(k,)] = els
        return groups

        
    
    def ungroup_old(self) -> typing.List[typing.Tuple[typing.Tuple[typing.Hashable], T]]:
        elements = list()
        for k,els in self.items():
            if hasattr(els, 'ungroup_recursive'):
                for ks, e in els.ungroup_recursive():
                    print(k, ks)
                    elements.append(((k,)+ks, e))
            else:
                for e in els:
                    elements.append(((k,), e))
        return elements
    
    def ungroup_recursive(self) -> typing.List[typing.Tuple[typing.List[typing.Hashable], T]]:
        elements = list()
        for k,els in self.items():
            if hasattr(els, 'ungroup_recursive'):
                for ks, e in els.ungroup_recursive():
                    elements.append(([k]+ks, e))
            else:
                for e in els:
                    elements.append(([k], e))
        return elements

def groupby(
        elements: typing.Iterable[T], 
        keys: typing.List[typing.Callable[[T], typing.Hashable]],
    ) -> GroupedData:
    '''Groups elements of the list into nested dictionaries according to group funcs.'''
    return GroupedData.group_elements(elements, keys)

