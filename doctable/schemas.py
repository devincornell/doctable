
import sqlalchemy as sa

from .coltypes import CpickleType, ParseTreeType, PickleFileType, TextFileType, FileTypeBase, JSONType


column_type_map = {
    'biginteger':sa.BigInteger,
    'boolean':sa.Boolean,
    'date':sa.Date,
    'datetime':sa.DateTime,
    'enum':sa.Enum,
    'float':sa.Float,
    'integer':sa.Integer,
    'interval':sa.Interval,
    'largebinary':sa.LargeBinary,
    'numeric':sa.Numeric,
    #'pickle':sa.PickleType,
    'smallinteger':sa.SmallInteger,
    'string':sa.String,
    'text':sa.Text,
    'time':sa.Time,
    'unicode':sa.Unicode,
    'unicodetext':sa.UnicodeText,
    'json': JSONType, # custom datatype
    'pickle': CpickleType, # custom datatype
    'parsetree': ParseTreeType, # custom datatype
    'picklefile': PickleFileType,
    'textfile': TextFileType,
}

def is_ord_sequence(obj):
    return isinstance(obj, list) or isinstance(obj,tuple)


def parse_schema(schema, default_fpath='./'):
    columns = list()
    for colinfo in schema:
        n = len(colinfo)
        if n not in (2,3,4):
            raise ValueError('A schema entry must have 2+ arguments: (type,name,..)')
        
        # column is regular type
        if colinfo[0] in column_type_map:
            coltype, colname = colinfo[:2]
            colargs = colinfo[2] if n > 2 else dict()
            coltypeargs = colinfo[3] if n > 3 else dict()
            if coltype in ('picklefile','textfile','jsonfile') and 'fpath' not in coltypeargs:
                coltypeargs['fpath'] = default_fpath+'_'+colname
            
            col = sa.Column(colname, column_type_map[coltype](**coltypeargs), **colargs)
            columns.append(col)
        else:
            if colinfo[0] == 'idcol': #shortcut for typical id integer primary key etc
                col = sa.Column(colinfo[1], sa.Integer, primary_key=True, autoincrement=True)
                columns.append(col)
            elif colinfo[0] == 'date_added': #shortcut for typical id integer primary key etc
                col = sa.Column(colinfo[1], sa.DateTime, default=datetime.now)
                columns.append(col)
            elif colinfo[0] == 'date_updated': #shortcut for typical id integer primary key etc
                col = sa.Column(colinfo[1], sa.DateTime, default=datetime.now, onupdate=datetime.now)
                columns.append(col)
            elif colinfo[0] == 'index':
                # ('index', 'ind0', ('name','address'),dict(unique=True)),
                indargs = colinfo[2] if n > 2 else dict()
                indkwargs = colinfo[3] if n > 3 else dict()
                ind = sa.Index(colinfo[1], *indargs, **indkwargs)
                columns.append(ind)
            elif colinfo[0] == 'check_constraint':
                # ('check_constraint','age >= 0 AND age < 120',, dict(name='age')),
                kwargs = colinfo[2] if n > 2 else dict()
                const = sa.CheckConstraint(colinfo[1], **kwargs)
                columns.append(const)
            elif colinfo[0] == 'unique_constraint':
                # ('unique_constraint', ('name','address'), dict(name='name_addr')),
                kwargs = colinfo[2] if n > 2 else dict()
                const = sa.UniqueConstraint(*colinfo[1], **kwargs)
                columns.append(const)
            elif colinfo[0] == 'primarykey_constraint':
                # ('primarykey_constraint', ('name','address'),dict(unique=True)),
                kwargs = colinfo[2] if n > 2 else dict()
                const = sa.PrimaryKeyConstraint(*colinfo[1], **kwargs)
                columns.append(const)
            elif colinfo[0] == 'foreignkey':
                if n < 3:
                    raise ValueError('A foreignkey constraint should follow the form '
                            '(\'foreignkey\', from_col(s), to_col(s), **kwargs).')
                
                fro = colinfo[1] if is_ord_sequence(colinfo[1]) else [colinfo[1]]
                to = colinfo[2] if is_ord_sequence(colinfo[2]) else [colinfo[2]]
                kwargs = colinfo[3] if n > 3 else dict()
                const = sa.ForeignKeyConstraint(fro, to, **kwargs)
                columns.append(const)
            else:
                raise ValueError('Column or constraint type "{}" was not recognized.'
                                ''.format(colinfo[0]))
            
    return columns



