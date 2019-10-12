# DocTable2
```python
DocTable2(self, schema=None, tabname='_documents_', fname=':memory:', engine='sqlite', persistent_conn=True, verbose=False, new_db=True, **engine_args)
```

## columns
Exposes SQLAlchemy core table columns object.
Notes:
    some info here:
    https://docs.sqlalchemy.org/en/13/core/metadata.html

    c = db.columns['id']
    c.type, c.name, c.
Returns:
    sqlalchemy columns: access to underlying columns
        object.

## primary_key
Returns primary key col name.
Notes:
    Returns first primary key where multiple primary
        keys exist (should be updated in future).

## schemainfo
Get info about each column as a dictionary.
Returns:
    dict<dict>: info about each column.

## table
Returns underlying sqlalchemy table object for manual manipulation.

## tabname
Gets name of table for this connection.
## close_conn
```python
DocTable2.close_conn(self)
```
Closes connection to db (if one exists).
Notes:
    Primarily to be used if persistent_conn flag was set
        to true in constructor, but user wants to close.

## open_conn
```python
DocTable2.open_conn(self)
```
Opens connection to db (if one does not exist).
Notes:
    Primarily to be used if persistent_conn flag was set
        to false in constructor, but user wants to create.


## count
```python
DocTable2.count(self, where=None, whrstr=None, **kwargs)
```
Count number of rows which match where condition.
Notes:
    Calls select_first under the hood.
Args:
    where (sqlalchemy condition): filter rows before counting.
    whrstr (str): filter rows before counting.
Returns:
    int: number of rows that match "where" and "whrstr" criteria.

## next_id
```python
DocTable2.next_id(self, idcol='id', **kwargs)
```
Returns the highest value in idcol plus one.
Args:
    idcol (str): column name to look up.
Returns:
    int: next id to be assigned by autoincrement.

## schemainfo_long
```python
DocTable2.schemainfo_long(self)
```
Get custom-selected schema information.
Notes:
    This method is similar to schemainfo, but includes
        more hand-selected information. Likeley to be
        removed in future versions.
Returns:
    dict<dict>: info about each column, more info than
        .schemainfo() provides.

## insert
```python
DocTable2.insert(self, rowdat, ifnotunique='fail', **kwargs)
```
Insert a row or rows into the database.
Args:
    rowdat (list<dict> or dict): row data to insert.
    ifnotunique (str): way to handle inserted data if it breaks
        a table constraint. Choose from FAIL, IGNORE, REPLACE.
Returns:
    sqlalchemy query result object.

## select_first
```python
DocTable2.select_first(self, *args, **kwargs)
```
Perform regular select query returning only the first result.
Args:
    *args: args to regular .select() method.
    **kwargs: args to regular .select() method.
Returns:
    sqlalchemy results obect: First result from select query.
Raises:
    LookupError: where no items are returned with the select
        statement. Couldn't return None or other object because
        those could be valid objects in a single-row select query.
        In cases where uncertain if row match exists, use regular
        .select() and count num results, or use try/catch.

## select_df
```python
DocTable2.select_df(self, cols=None, *args, **kwargs)
```
Select returning dataframe.
Args:
    cols: sequence of columns to query. Must be sequence,
        passed directly to .select() method.
    *args: args to regular .select() method.
    **kwargs: args to regular .select() method.
Returns:
    pandas dataframe: Each row is a database row,
        and output is not indexed according to primary
        key or otherwise. Call .set_index('id') on the
        dataframe to envoke this behavior.

## select_series
```python
DocTable2.select_series(self, col, *args, **kwargs)
```
Select returning pandas Series.
Args:
    col: column to query. Passed directly to .select()
        method.
    *args: args to regular .select() method.
    **kwargs: args to regular .select() method.
Returns:
    pandas series: enters rows as values.

## select
```python
DocTable2.select(self, cols=None, where=None, orderby=None, groupby=None, limit=None, whrstr=None, offset=None, **kwargs)
```
Perform select query, yield result for each row.

Description: Because output must be iterable, returns special column results
    by performing one query per row. Can be inefficient for many smaller
    special data information.

Args:
    cols: list of sqlalchemy datatypes created from calling .col() method.
    where (sqlachemy BinaryExpression): sqlalchemy "where" object to parse
    orderby: sqlalchemy orderby directive
    groupby: sqlalchemy gropuby directive
    limit (int): number of entries to return before stopping
    whrstr (str): raw sql "where" conditionals to add to where input
Yields:
    sqlalchemy result object: row data

## select_chunk
```python
DocTable2.select_chunk(self, cols=None, chunksize=1, max_rows=None, **kwargs)
```
Performs select while querying only a subset of the results at a time.
Args:
    cols (col name(s) or sqlalchemy object(s)): columns to query
    chunksize (int): size of individual queries to be made. Will
        load this number of rows into memory before yielding.
    max_rows (int): maximum number of rows to retrieve. Because
        the limit argument is being used internally to limit data
        to smaller chunks, use this argument instead. Internally,
        this function will load a maximum of max_rows + chunksize
        - 1 rows into memory, but yields only max_rows.
Yields:
    sqlalchemy result: row data - same as .select() method.

## update
```python
DocTable2.update(self, values, where=None, whrstr=None, **kwargs)
```
Update row(s) assigning the provided values.
Args:
    values (dict<colname->value> or list<dict> or list<(col,value)>)):
        values to populate rows with. If dict, will insert those values
        into all rows that match conditions. If list of dicts, assigns
        expression in value (i.e. id['year']+1) to column. If list of
        (col,value) 2-tuples, will assign value to col in the order
        provided. For example given row values x=1 and y=2, the input
        [(x,y+10),(y,20)], new values will be x=12, y=20. If opposite
        order [(y,20),(x,y+10)] is provided new values would be y=20,
        x=30. In cases where list<dict> is provided, this behavior is
        undefined.
    where (sqlalchemy condition): used to match rows where
        update will be applied.
    whrstr (sql string condition): matches same as where arg.
Returns:
    SQLAlchemy result proxy object

## delete
```python
DocTable2.delete(self, where=None, whrstr=None, vacuum=False, **kwargs)
```
Delete rows from the table that meet the where criteria.
Args:
    where (sqlalchemy condition): criteria for deletion.
    whrstr (sql string): addtnl criteria for deletion.
    vacuum (bool): will execute vacuum sql command to reduce
        storage space needed by SQL table. Use when deleting
        significant ammounts of data.
Returns:
    SQLAlchemy result proxy object.

## execute
```python
DocTable2.execute(self, query, verbose=None, **kwargs)
```
Execute an sql command. Called by most higher-level functions.
Args:
    query (sqlalchemy condition or str): query to execute;
        can be provided as sqlalchemy condition object or
        plain sql text.
    verbose (bool or None): Print SQL command issued before
        execution.

## col
```python
DocTable2.col(self, name)
```
Accesses a column object. Equivalent to table.c[name].
Args:
    Name of column to access. Applied as subscript to
        sqlalchemy columns object.

## select_bootstrap
```python
DocTable2.select_bootstrap(self, *args, **kwargs)
```
Performs select statement by bootstrapping output.
Notes:
    This is a simple wrapper over .select_bootstrap_iter(),
        simply casting to a list before returning.
Args:
    *args: passed to .select_bootstrap_iter() method.
    **kwargs: passed to .select_bootstrap_iter() method.
Returns:
    list: result rows

## select_bootstrap_iter
```python
DocTable2.select_bootstrap_iter(self, cols=None, nsamp=None, where=None, idcol=None, whrstr=None, **kwargs)
```
Bootstrap (sample with replacement) from database.
Notes:
    This should be used in cases where the order of returned elements
        does not matter. It works internally by selecting primary key
        (idcol), sampling with replacement using python, and then performing
        select queries where idcol in (selected ids). Number of queries varies
        by the maximum count of ids which were sampled.
Args:
    cols (sqlalchemy column names or objects): passed directly to
        .select().
    nsamp (int): number of rows to sample with replacement.
    where (sqlalchemy condition): where criteria.
    whrstr (str): SQL command to conditionally select
    idcol (col name or object): Must be unique id assigned to each
        column. Extracts first primary key by default.
Yields:
    sqlalchemy row objects: bootstrapped rows (order not gauranteed).

