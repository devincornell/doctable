import sqlalchemy
import dataclasses
import typing
import pandas as pd


from ..doctable import DocTable
from ..schemas import DocTableSchema
from .selectqueryargs import SelectQueryArgs
from ..util import is_sequence

class ObjectIsNotSchemaClass(TypeError):
    pass

SingleColumn = typing.Union[str, sqlalchemy.Column]
ColumnList = typing.List[SingleColumn]

@dataclasses.dataclass
class Query:
    dtab: DocTable
    
    ######################################## Select ########################################
        
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
            cols = self.parse_col(col),
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
            raw_result = True,
        )
        return [r[0] for r in rows]
        
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
    
    def parse_col(self, col: SingleColumn) -> typing.List[sqlalchemy.Column]:
        if is_sequence(col):
            raise TypeError('col argument should be single column.')
        
        use_col = self.dtab.col(col) if isinstance(col,str) else col
        return [use_col]

    ############################## General Purpose ##############################

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

    




