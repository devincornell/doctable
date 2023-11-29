# Installation and Change Log

`doctable` is on PyPI, so you can install it with `pip`:

For sqlalchemy >= 2.0: `pip install doctable==2.0`

For sqlalchemy <= 1.4: `pip install doctable==1.0`


## Changes in Version 2.0

+ Create database connections using `ConnectCore` objects instead of `ConnectEngine` or `DocTable` objects.

+ Database tables represented by `DBTable` objects instead of `DocTable` objects. All `DBTable` instances originate from a `ConnectCore` object.

+ Create schemas using the `doctable.table_schema` decorator instead of the `doctable.schema` decorator. This new decorator includes constraint and index parameters as well as those for the `dataclass` objects.

+ The `Column` function replaces `Col` as generic default parameter values with more fine-grained control over column properties. This function provides a clearer separation between parameters that affect the behavior of the object as a dataclass (supplied as a `FieldArgs` object) and those that affect the database column schema (supplied via a `ColumnArgs` object).

+ **New command line interface**: you may execute doctable functions through the command line. Just use `python -m doctable execute {args here}` to see how to use it.



