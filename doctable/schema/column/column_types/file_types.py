from __future__ import annotations

import dataclasses
import typing
import pickle
#import sqlalchemy.types as types
import sqlalchemy
import numpy as np
from random import randrange
import os
import json
import pathlib
import hashlib

class FileTypeBase(sqlalchemy.types.TypeDecorator):
    '''Base class for file types. Stores data in files and records'''
    impl = sqlalchemy.types.String # just stores filename internally
    
    def __init__(self, file_type_control: FileTypeControl, *arg, **kwargs):
        self.control = file_type_control
        self.control.create_folder()
        
        super().__init__(self, *arg, **kwargs)
    
    ################# Used by sqlalchemy #################    
    def process_bind_param(self, value: typing.Any, dialect: str):
        if value is not None:
            return self.write_data(value, self.control, dialect)
        else:
            return None
    
    def process_result_value(self, hash_value: bytes, dialect: str):
        if self.control.raw:
            return hash_value
        elif hash_value is not None: # it is a valid hash
            return self.read_data(hash_value, self.control, dialect)
        else:
            return None
        
    ################# Implemented by Subclass #################
    @classmethod
    def write_data(cls, data: typing.Any, control: FileTypeControl, dialect: str) -> bytes:
        '''Write file and return hash of new file.'''
        raise NotImplementedError
    
    @classmethod
    def read_data(cls, hash_value: bytes, control: FileTypeControl, dialect: str) -> typing.Any:
        '''Read data given the control and hash information.'''
        raise NotImplementedError


class TextFileType(FileTypeBase):
    @classmethod
    def write_data(cls, data: str, control: FileTypeControl, dialect: str) -> bytes:
        hash_value = control.get_md5(data)
        if not control.exists(hash_value):
            with control.open(hash_value, 'w') as f:
                f.write(data)
        return hash_value
    
    @classmethod
    def read_data(cls, hash_value: bytes, control: FileTypeControl, dialect: str) -> str:
        with control.open(hash_value, 'rb') as f:
            return f.read()

class PickleFileType(FileTypeBase):
    @classmethod
    def write_data(cls, data: typing.Any, control: FileTypeControl, dialect: str) -> bytes:
        pickle_bytes = pickle.dumps(data)
        hash_value = control.get_md5(pickle_bytes)
        if not control.exists(hash_value):
            with control.open(hash_value, 'wb') as f:
                f.write(pickle_bytes)
        return hash_value
    
    @classmethod
    def read_data(cls, hash_value: bytes, control: FileTypeControl, dialect: str) -> str:
        with control.open(hash_value, 'rb') as f:
            return pickle.load(f)

class JSONFileType(FileTypeBase):
    @classmethod
    def write_data(cls, data: typing.Dict, control: FileTypeControl, dialect: str) -> bytes:
        json_str = json.dumps(data)
        hash_value = control.get_md5(json_str)
        if not control.exists(hash_value):
            with control.open(hash_value, 'w') as f:
                f.write(json_str)
        return hash_value
    
    @classmethod
    def read_data(cls, hash_value: bytes, control: FileTypeControl, dialect: str) -> typing.Any:
        with control.open(hash_value, 'r') as f:
            return json.load(f)


@dataclasses.dataclass
class FileTypeControl:
    '''Controls behavior of a given file type.'''
    path: pathlib.Path # path to folder where files are stored
    raw: bool # access raw filenames instead of data

    def exists(self, fname: str) -> bool:
        return self.joinpath(fname).exists()

    def open(self, fname: str, mode: str) -> typing.IO:
        return self.joinpath(fname).open(mode)

    def joinpath(self, fname):
        return self.path.joinpath(fname)
    
    def create_folder(self):
        self.path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_md5(dumped_string: typing.Hashable):
        return hashlib.md5(dumped_string).hexdigest()
    
    