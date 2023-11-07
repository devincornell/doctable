from __future__ import annotations

import typing
import dataclasses
import sqlalchemy

def ForeignKey(
        local_columns: typing.List[str], 
        from_columns: typing.List[str], 
        onupdate: typing.Literal['CASCADE','RESTRICT','SET NULL','NO ACTION','SET DEFAULT'] = 'NO ACTION',
        ondelete: typing.Literal['CASCADE','RESTRICT','SET NULL','NO ACTION','SET DEFAULT'] = 'NO ACTION',
        **kwargs: typing.Dict[str, typing.Any],
    ) -> sqlalchemy.ForeignKeyConstraint:
    '''Create a foreign key constraint on some columns.
        https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.ForeignKeyConstraint
        https://docs.sqlalchemy.org/en/20/core/constraints.html
        NOTE from docs: It’s important to note that the ForeignKeyConstraint is 
        the only way to define a composite foreign key. While we could also have 
        placed individual ForeignKey objects on both the invoice_item.invoice_id 
        and invoice_item.ref_num columns, SQLAlchemy would not be aware that these 
        two values should be paired together - it would be two individual foreign 
        key constraints instead of a single composite foreign key referencing two 
        columns.
    '''
    return sqlalchemy.ForeignKeyConstraint(
        columns=local_columns,
        refcolumns=from_columns,
        onupdate=onupdate,
        ondelete=ondelete,
        **kwargs,
    )

def CheckConstraint(
        sqltext: str,
        name: typing.Optional[str] = None,
        **kwargs: typing.Dict[str, typing.Any],
    ) -> sqlalchemy.CheckConstraint:
    '''Create a check constraint on some columns.
        https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.CheckConstraint
    '''
    return sqlalchemy.CheckConstraint(
        sqltext=sqltext,
        name=name,
        **kwargs,
    )

def UniqueConstraint(
        *column_names: typing.List[str],
        name: typing.Optional[str] = None,
        **kwargs: typing.Dict[str, typing.Any],
    ) -> sqlalchemy.UniqueConstraint:
    '''Create a unique constraint on some columns.
        https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.UniqueConstraint
    '''
    return sqlalchemy.UniqueConstraint(
        *column_names,
        name=name,
        **kwargs,
    )

def PrimaryKeyConstraint(
        *column_names: typing.List[str],
        name: typing.Optional[str] = None,
        **kwargs: typing.Dict[str, typing.Any],
    ) -> sqlalchemy.PrimaryKeyConstraint:
    '''Create a primary key constraint on some columns.
        https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.PrimaryKeyConstraint
    '''
    return sqlalchemy.PrimaryKeyConstraint(
        *column_names,
        name=name,
        **kwargs,
    )


