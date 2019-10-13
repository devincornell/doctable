
from datetime import datetime

import sys
sys.path.append('..')
import doctable as dt

schema = (
    # classic id column
    ('id', 'integer', dict(autoincrement=True, primary_key=True)),
    
    #SQLAlchemy: Column('age', Integer), Column('fav_color', String)
    ('age', 'integer', dict(nullable=False)),
    ('fav_color', 'string'),
    
    #SQLAlchemy: Column('name', String(length=500), default='')
    ('name', 'string', dict(default=''), dict(length=100)),
    
    #SQLAlchemy: Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
    ('updated_on', 'datetime', dict(default=datetime.now, onupdate=datetime.now)),
    ('created_on', 'datetime', dict(default=datetime.now)),
    
    # custom types
    # TokensType and ParagraphsType are defined in doctable/coltypes.py
    # SQLAlchemy: Column('tokenized', TokensType), Column('sentencized', ParagraphsType)
    ('sentencized','subdocs'),
    ('tokenized','tokens'),
)

constraints = (
    #SQLAlchemy: CheckConstraint('age > 0')
    ('check','age > 0'),
    
    #SQLAlchemy: CheckConstraint('color in ("RED","BLUE")')
    ('check','fav_color in ("RED","BLUE")'),
    
    # make sure each category/title entry is unique
    #SQLAlchemy:  UniqueConstraint('name', 'age', name='work_key')
    ('unique','name', 'age'),
)

indexes = (
    ('ind0', 'name', 'age', dict(unique=True)),
)


if __name__ == '__main__':
    
    md = dt.DocTable2(schema, constraints, indexes)
    print(md)
    
    '''
    # failed attempt to test foreign keys
    
    fname='tmp5.db'
    schema2 = (
        ('fkid', 'integer', dict(primary_key=True)),
        ('other','string'),
    )
    constraints2 = [('foreignkey',['fkid'], ['docs1.id'], dict(onupdate="CASCADE", ondelete="CASCADE"))]
    
    md2 = dt.DocTable2(schema=schema2, constraints=constraints2, fname=fname, tabname='docs2', verbose=True)
    q = md2.execute('SELECT COUNT(*) FROM docs1')
    print(next(q))
        
    '''