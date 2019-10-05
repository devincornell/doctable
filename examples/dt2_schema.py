
from datetime import datetime
import random

import sys
sys.path.append('..')
from doctable import DocTable2

class MyDocuments(DocTable2):
    '''Class providing schema for MyDocuments database.
    '''
    
    # provide schema information
    # each schema element can be a 
    tabname = 'mydocuments'
    schema = (
        # standard id column
        #SQLAlchemy: Column('id', Integer, primary_key = True, autoincrement=True), 
        ('id','integer',dict(primary_key=True, autoincrement=True)),

        # make a category column with two options: "FICTION" and "NONFICTION"
        #SQLAlchemy: Column('title', String,)
        #SQLAlchemy: CheckConstraint('category in ("FICTION","NONFICTION")', name='salary_check')
        ('category','string', dict(nullable=False)),
        ('category in ("FICTION","NONFICTION")','check_constraint', dict(name='salary_check')),

        # make a non-null title column
        #SQLAlchemy: Column('title', String,)
        ('title','string', dict(nullable=False)),

        # make sure each category/title entry is unique
        #SQLAlchemy:  UniqueConstraint('category', 'title', name='work_key')
        (['category','title'],'unique_constraint',dict(name='work_key')),

        # make an abstract where the default is an empty string instead of null
        #SQLAlchemy: Column('abstract', String, default='')
        ('abstract','string', dict(default='')),

        # make an age column where age must be greater than zero
        #SQLAlchemy: Column('abstract', Integer)
        #SQLAlchemy: CheckConstraint('age > 0')
        ('age','integer'),
        ('age > 0','check_constraint'),

        # make a column that keeps track of column updates
        #SQLAlchemy: Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
        ('updated_on', 'datetime', dict(default=datetime.now, onupdate=datetime.now)),

        # make a string column with max of 500 characters
        #SQLAlchemy: Column('abstract', String, default='')
        ('text','string',dict(),dict(length=500)),
        
        # make index table
        # SQLAlchemy: Index('ind0', 'category', 'title', unique=True)
        ('ind0', 'index', ('category','title'),dict(unique=True)),
        
        # make this id a foreign key to another table column (CAN'T SHOW HERE)
        # SQLAlchemy: ForeignKeyConstraint(['id'], ['invoice.invoice_id',], onupdate="CASCADE", ondelete="CASCADE")
        #((['id'],['othertablerefid']), 'foreignkey_constraint',dict(),dict(onupdate="CASCADE", ondelete="CASCADE")),
        
        # try out custom data types
        # TokensType and ParagraphsType are defined in doctable/coltypes.py
        # SQLAlchemy: Column('tokenized', TokensType), Column('sentencized', ParagraphsType)
        ('sentencized','subdocs'),
        ('tokenized','tokens'),

    )
    
    def __init__(self, fname=':memory:', engine='sqlite', verbose=False):
        '''Provides a simpler (or more complex) interface to the DocTable2 constructor.
        '''
        super().__init__(
            self.schema, 
            tabname=self.tabname, 
            fname=fname,
            engine=engine,
            verbose=verbose,
        )
    
    
    
if __name__ == '__main__':
    md = MyDocuments(verbose=True)
    print(md)
    
    
