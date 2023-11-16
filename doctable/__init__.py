'''
## `doctable` Python Package

See the [doctable website](https://devinjcornell.com/doctable/) for documentation and examples.

Created by [Devin J. Cornell](https://devinjcornell.com).

---

## Doctable has a new interface!

The package has been updated with an entirely new API to improve on previous limitations and better match the [Sqlalchemy 2.0](https://www.sqlalchemy.org/) interface. Inspired by the [attrs project](https://www.attrs.org/en/stable/names.html), I used different names for functions and classes to make it clear that the interface has changed and open the possibility for backwards compatibility with upgraded internals in the future. 

For now, stick to installing from the `legacy` branch when using sqlalchemy <= 1.4, and the `master` branch for sqlalchemy >= 2.0.

---

## Installation

From [Python Package Index](https://pypi.org/project/doctable/): `pip install doctable`

For sqlalchemy >= 2.0: `pip install --upgrade git+https://github.com/devincornell/doctable.git@master`

For sqlalchemy <= 1.4: `pip install --upgrade git+https://github.com/devincornell/doctable.git@legacy`

---

## Changes in Version 2.0

+ Create database connections using `ConnectCore` objects instead of `ConnectEngine` or `DocTable` objects.

+ Database tables represented by `DBTable` objects instead of `DocTable` objects. All `DBTable` instances originate from a `ConnectCore` object.

+ Create schemas using the `doctable.table_schema` decorator instead of the `doctable.schema` decorator. This new decorator includes constraint and index parameters as well as those for the `dataclass` objects.

+ The `Column` function replaces `Col` as generic default parameter values with more fine-grained control over column properties. This function provides a clearer separation between parameters that affect the behavior of the object as a dataclass (supplied as a `FieldArgs` object) and those that affect the database column schema (supplied via a `ColumnArgs` object).

+ **New command line interface**: you may execute doctable functions through the command line. Just use `python -m doctable execute {args here}` to see how to use it.

---

## Examples

See the `examples/` directory for more detailed examples.

### Basic steps

These are the basic steps for using `doctable` to create a database connection, define a schema, and execute queries. For more examples, see the [doctable website](https://doctable.org).

**1. Create a database connection.**

```python
core = doctable.ConnectCore.open(
    target=':memory:', # use a filename for a sqlite to write to disk
    dialect='sqlite',
)
```

**2. Define a database schema from a dataclass.**

```python
@doctable.table_schema
class MyContainer:
    name: str
    age: int
    id: int = doctable.Column(
        column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True),
    )

```

**3. Emit DDL to create a table from the schema.**

```python
with core.begin_ddl() as emitter:
    tab0 = emitter.create_table(container_type=MyContainer)
pprint.pprint(core.inspect_columns('MyContainer'))
```

**4. Execute queries on the table.**

```python
with tab1.query() as q:
    q.insert_single(MyContainer(name='devin', age=40))
    print(q.select())

>> MyContainer(name='devin', age=40, id=1)
```


'''

name = "doctable"

from .connectcore import ConnectCore, TableAlreadyExistsError, TableDoesNotExistError
from .query import *
from .schema import *
from .dbtable import *
from .exposed import *



#class f:
#    #sqlalchemy.sql.func
#    max = sqlalchemy.sql.func.max
#    min = sqlalchemy.sql.func.min
#    count = sqlalchemy.sql.func.count
#    sum = sqlalchemy.sql.func.sum
#
#    distinct = sqlalchemy.sql.expression.distinct
#    between = sqlalchemy.sql.expression.between
#    
#    all_ = sqlalchemy.sql.expression.all_
#    and_ = sqlalchemy.sql.expression.and_
#    or_ = sqlalchemy.sql.expression.or_
#    not_ = sqlalchemy.sql.expression.not_
#
#    desc = sqlalchemy.sql.expression.desc
#    asc = sqlalchemy.sql.expression.asc
#    
#    any_ = sqlalchemy.sql.expression.any_
#    alias = sqlalchemy.sql.expression.alias
#    between = sqlalchemy.sql.expression.between


