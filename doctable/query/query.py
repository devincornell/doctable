import sqlalchemy
import dataclasses
import typing
import pandas as pd


from ..doctable import DocTable
from ..schemas import DocTableSchema
from ..util import is_sequence

from .selectqueryargs import SelectQueryArgs
from .errors import *


SingleColumn = typing.Union[str, sqlalchemy.Column]
ColumnList = typing.List[SingleColumn]

typing.Literal['FAIL', 'IGNORE', 'REPLACE']

@dataclasses.dataclass
class Query:
    dtab: DocTable
    
    ######################################## High-level inserts that infer type. ########################################
    def insert(self, 
            rowdat: typing.Union[DocTableSchema, typing.Dict, typing.List[typing.Union[DocTableSchema, typing.Dict]]], 
            ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail',
        ) -> sqlalchemy.engine.ResultProxy:
        '''Insert a row or rows into the database.
        Args:
            rowdat (list<dict> or dict): row data to insert.
            ifnotunique (str): way to handle inserted data if it breaks
                a table constraint. Choose from FAIL, IGNORE, REPLACE.
        Returns:
            sqlalchemy query result object.
        '''
        if is_sequence(rowdat):
            return self.insert_many(rowdat, ifnotunique=ifnotunique)
        else:
            return self.insert_single(rowdat, ifnotunique=ifnotunique)

    
    def insert_single(self, 
            rowdata: typing.Union[DocTableSchema, typing.Dict], 
            ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail',
        ) -> sqlalchemy.engine.ResultProxy:
        '''Insert a single row into the database.
        '''
        if isinstance(rowdata, DocTableSchema) and self.dtab._schema_is_obj():
            return self.q.insert_object(rowdata, ifnotunique=ifnotunique)
        else:
            return self.q.insert_dict(rowdata, ifnotunique=ifnotunique)

    def insert_many(self, 
            rowdata: typing.List[typing.Union[DocTableSchema, typing.Dict]], 
            ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail'
        ) -> sqlalchemy.engine.ResultProxy:
        '''Insert multiple rows into the database, infer type.'''
        if isinstance(rowdata[0], DocTableSchema) and self.dtab._schema_is_obj():
            return self.insert_objects(rowdata, ifnotunique=ifnotunique)
        else:
            return self.insert_dicts(rowdata, ifnotunique=ifnotunique)
    
    ######################################## Insert Multiple ########################################
    def insert_objects(self, 
            schema_objs: typing.List[DocTableSchema], 
            ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail'
        ) -> sqlalchemy.engine.ResultProxy:
        '''Insert multiple rows as objects into the db.'''
        self._check_readonly('insert_objects')
        if not is_sequence(schema_objs):
            raise TypeError('insert_objects needs a list or tuple of schema objects.')
        obj_dicts = [self._schema_obj_to_dict(o) for o in schema_objs]
        return self.insert_dicts(obj_dicts, ifnotunique=ifnotunique)
        
    def insert_dicts(self, 
            datum: typing.List[typing.Dict[str, typing.Any]], 
            ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail'
        ) -> sqlalchemy.engine.ResultProxy:
        '''Insert multiple rows as dictionaries into the db.'''
        self._check_readonly('insert_dicts')
        if not is_sequence(datum):
            raise TypeError('insert_dicts needs a list or tuple of schema objects.')
        q = self.query(ifnotunique=ifnotunique)
        return self.insert_query(q, datum)

    ######################################## Insert Single ########################################
    def insert_object(self, obj: DocTableSchema, ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail', **kwargs) -> sqlalchemy.engine.ResultProxy:
        self._check_readonly('insert_object')
        obj_dict = self._schema_obj_to_dict(obj)
        return self.insert_dict(obj_dict, ifnotunique=ifnotunique)

    def insert_dict(self, data: typing.Dict[str, typing.Any], ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail') -> sqlalchemy.engine.ResultProxy:
        self._check_readonly('insert_dict')
        q = self.query(ifnotunique=ifnotunique)
        return self.insert_query(q, data)

    ######################################## Build Insert Query ########################################
    def insert_query(self, ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail') -> sqlalchemy.sql.Insert:
        q: sqlalchemy.sql.Select = sqlalchemy.sql.insert(self.dtab.table)
        q = q.prefix_with('OR {}'.format(ifnotunique.upper()))
        return q
    
    
    ######################################## Pandas Select ########################################
    
    def count(self, where=None, wherestr=None, **kwargs) -> int:
        ''''''
        cter = sqlalchemy.func.count()
        ct = self.select_first(cter, where=where, wherestr=wherestr, **kwargs)
        return ct
    
    def select_head(self, n: int = 5, **kwargs) -> pd.DataFrame:
        return self.select_df(limit=n, **kwargs)
        
    def select_series(self,
            col: SingleColumn,
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            limit: int = None,
            wherestr: str = None,
            offset: int = None,
        ) -> pd.Series:
        
        return pd.Series(self.select_col(
            col = col,
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
        ))
        
    def select_df(self, 
            cols: ColumnList,
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            limit: int = None,
            wherestr: str = None,
            offset: int = None,
        ) -> pd.DataFrame:
        
        return pd.DataFrame(self.select_base(
            cols = self.parse_input_cols(cols),
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
            raw_result = True,
        ))
        
    ######################################## Single-column Select ########################################
    
    def select_col(self, 
            col: SingleColumn,
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            limit: int = None,
            wherestr: str = None,
            offset: int = None,
        ) -> typing.List[typing.Any]:
        '''Select values of a single column.'''
        
        rows = self.select_base(
            cols = self.parse_input_col(col),
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
            raw_result = True,
        )
        return [r[0] for r in rows]

    ######################################## Base Selection Funcs ########################################
    def select_first(self,
            cols: ColumnList,
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            wherestr: str = None,
            offset: int = None,
        ) -> pd.Series:
        
        results = self.select_base(
            cols = cols,
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = 1,
            wherestr = wherestr,
            offset = offset,
        )
        
        if len(results) == 0:
            raise LookupError('No results were returned. Needed to error '
                'so this result wasn not confused with case where actual '
                'result is None. If not sure about result, use regular '
                '.select() method with limit=1.')

        return results[0]

    def select_base(self, 
            cols: typing.List[sqlalchemy.Column],
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            limit: int = None,
            wherestr: str = None,
            offset: int = None,
            raw_result: bool = False,
        ) -> typing.List[typing.Dict[str, typing.Any]]:
        '''
        Select some basic shit.
        Description: Because output must be iterable, returns special column results 
            by performing one query per row. Can be inefficient for many smaller 
            special data information.
        
        Args:
            cols: list of sqlalchemy datatypes created from calling .col() method.
            where (sqlachemy BinaryExpression): sqlalchemy "where" object to parse
            orderby: sqlalchemy orderby directive
            groupby: sqlalchemy gropuby directive
            limit (int): number of entries to return before stopping
            wherestr (str): raw sql "where" conditionals to add to where input
            as_dataclass (bool): if schema was provided in dataclass format, should return as 
                dataclass object?
            **kwargs: passed to self.execute()
        Yields:
            sqlalchemy result object: row data

        '''
        q = SelectQueryArgs(
            cols = self.parse_input_cols(cols),
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
        ).get_query()
        
        result = self.dtab.execute(q)
        if raw_result:
            return result.fetchall()
        else:
            return [self.dtab.schema.parse_row(r) for r in result.fetchall()]

    ############################## Parse User Input ##############################
    def parse_input_cols(self, cols: ColumnList) -> typing.List[sqlalchemy.Column]:
        '''Pass variable passed to cols.'''
        if not is_sequence(cols):
            raise TypeError('col argument should be single column.')
        
        if cols is None:
            cols = list(self.dtab.columns)
                
        cols = [self.dtab.col(c) if isinstance(c,str) else c for c in cols]
        
        return cols
    
    def parse_input_col(self, col: SingleColumn) -> typing.List[sqlalchemy.Column]:
        if is_sequence(col):
            raise TypeError('col argument should be single column.')
        
        use_col = self.dtab.col(col) if isinstance(col,str) else col
        return [use_col]

    ############################## General Purpose ##############################

    def _check_readonly(self, funcname: str) -> None:
        if self.readonly:
            raise SetToReadOnlyMode(f'Cannot call .{funcname}() when doctable set to readonly.')

    def _schema_obj_to_dict(self, obj: DocTableSchema) -> typing.Dict[str, typing.Any]:
        '''Convert schema object to a dictionary.'''
        try:
            return obj._doctable_as_dict()
        except AttributeError as e:
            e2 = ObjectIsNotSchemaClass(f'Object of type {type(obj)} '
                'should be of type DocTableSchema.')
            raise e2 from e
        
    def _dict_to_schema_obj(self, data: typing.Dict[str, typing.Any]) -> DocTableSchema:
        '''Convert dictionary to schema object.'''
        return self.dtab.schema._doctable_from_db(data)

    




