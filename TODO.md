

# stuff to do

+ check out table.create() to make tables without metadata.create_all() - it's a good alternative
    + mentioned in init autoincrement here: https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.Column.__init__
    + definition here: https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.Table.create
    + maybe add table.delete( )as well?
+ add "order" parameter to allow setting id column last in object (still need to figure out default value situation)
+ separate dataclass and column value defaults. make a parameter for each
+ lay out db column parameters in Column() function
    + see init arguments here: https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.Column.__init__
    + especially see "default" as an sqlalchemy default vs the dataclasses default
    + instead of laying out all params, consider creating parameter objects with definitions. Might work fine for type hints actually.
        + i.e. 


