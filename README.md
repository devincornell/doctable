

# DocTable Package for Python

Object-based database access specifically intended for text analysis applications.

The package makes it easy to create a new sqlite data table with simple schemas; a common task in many text analysis projects. The package consists primarily of two classes: the original **DocTable**, built directly as a thin interface to the sqlite3 package, and **DocTable2**, the successor which is implemented using SQLAlchemy.

The typical way to use this package is to create new classes which inherit from DocTable2 or DocTable. These classes can manage schema info and allow users to add application-specific member functions for convenient access to the underlying database which benefit from useful methods built into DocTable.

These classes are intended to provide an object-oriented interface to single-table database schemas which are designed to be in-synch with databases. If the schema of the class object changes, it can be more difficult to access data in a database which was created using a different schema. As such, it can be helpful to version database interfaces with different schemas.

## DocTable2 Class

**DocTable2** is built on SQLAlchemy, a flexible object-oriented interface to many mainstream DB engines. The class is inspired by the object-based interface of SQLAlchemy but makes it easier to access SQLAlchemy features without importing a large number of database objects. The interface requires much less user code compared to SQLAlchemy, taking cues from the original Doctable class.

### DocTable2 Schema

Often the **DocTable2** is used by subclassing. The subclass typically will store the table schema and custom args can accept filename or engine. This example below shows a doctable called `MyDocuments` where the table name is `mydocuments` with three columns: `id` (commonly added for unique row identification), `name` of string type, and `age` of integer type. This approach also allows the user to 

    ```python

    import doctable as dt
    class MyDocuments(dt.DocTable2):
        tabname = 'mydocuments'
        schema = (
            ('id','integer',dict(primary_key=True, autoincrement=True)),
            ('name','string', dict(nullable=False, unique=True)),
            ('age','integer'),
        )

        def __init__(self, fname=':memory:', engine='sqlite', verbose=False):
            super().__init__(
                self.schema, 
                tabname=self.tabname, 
                fname=fname,
                engine=engine,
                verbose=verbose,
            )
    ```
    
### Special Data Types

A primary advantage of DocTable2 is that it manages separate tables which store custom "special" data type columns, but interfaces with these separate tables as if they were regular columns in the primary table. Managing this data in separate tables can provide several performance advantages over single-table schemas. Currently there are two implemented custom datatypes which take advantage of the multi-table schema feature:

* **bigpickle column type**: This column type stores large pickled Python objects in a separate table from the primary table automatically created by DocTable. The `.select_iter(`) method of DocTable2 will will perform a separate query for each row yield to minimize memory overhead and ensure the database does not queue the select query from that column. In contrast, the .select() method will perform one query to the bigblob table, collecting all python objects with a single query and automatically merge them with results from the primary document table.

* **subdoc column type**: This column type is for storing separate sub-document level token lists with one (document)-to-many (subdocs) relationships. This is primarily useful because of the frequent requirement to bootstrap text corpora at the sentence or paragraph (any sub-document) level - a useful feature for analyzing the sensitivity of a particular text analysis project to sub-document samples. The example below shows a schema which includes the two special column types to store other data.

    ```python
    schema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('name','string', dict(nullable=False, unique=True)),
        ('age','integer'),
        ('model','bigpickle'), # this data type will be stored in a separate file
        ('anothermodel','bigpickle'), # this data type will be stored in a separate file
        ('sentences','subdocs'), # this data type will be stored in a separate file
    )
    ```
The above schema definition will store in the primary document table (called `mydocuments`, for example) a special column named `_fk_special_` in addition to `id`, `name`, and `age` columns. It will store the data provided for the `model` and `anothermodel` columns in a separate table named `_mydocuments_bigpickles` (distinguished with a column named `col_name`), and teh data provided for `sentences` in a separate table named `_mydocuments_subdocs`. These special datatypes are handled opaquely by **DocTable2** and thus the user doesn't need to access the special table directly (and, in fact, probably should not). Note that because these columns are handled within a table, they cannot have assigned uniqueness or other constraints.

### DocTable2 Insert Method

There are three ways to insert data into a DocTable2 depending on the data provided to the `.insert()` method. Each call creates at least one `SELECT` request because of the need to increment a special, hidden column which is associated with the special column datatypes. Unfortunately this can be expensive.

1. Insert One
    This method is used when a single row is provided. The example below shows the insertion of a single row in each iteration of the loop. The method is expensive because eaach call makes a single `SELECT` request, a single `INSERT` request, and another `INSERT` request for each provided special datatype column. Example inserting 5k rows using this method: took 3.089451313018799 sec.

    ```python
    N = 5000
    for i in range(N):
        md.insert({'name':'user_'+str(i), 'age':random.random()})
    ```

2. Insert from Iterator

    The method is expensive because it makes a single `SELECT` call to get the next fkid and each iteration makes a single `INSERT` request, and another `INSERT` request for each provided special datatype column. Example inserting 5k rows using this method: took 1.6546974182128906 sec.

    ```python

    def get_users_iterator(N):
        for i in range(N):
            yield {'name':'user_'+str(i), 'age':random.random()}
    md.insert(get_users_iterator)
    ```

3. Insert from Sequence (list, tuple, or set)

    This approach is used when provided with a datatype which maintains the full set of data in memory. It is by far the fastest insert method, and should likely be used if the client computer has enough memory to store all rows in memory at once. The call makes a single `SELECT` request and a single `INSERT` request, plus one `INSERT` for each special column data provided. Example inserting 5k rows using this method: took 0.28697729110717773 sec.

    ```python
    rows = [{'name':'user_'+str(i), 'age':random.random()} for i in range(N)]
    md.insert(rows)
    ```
.








### Interface to SQLAlchemy

As DocTable2 is built on SQLAlchemy, many of the SQLAlchemy features are abstracted in a straightforward manner. For details on the conversion interface, see the [SQLAlchemy interface page](https://github.com/devincornell/doctable/blob/doctable2/sqlalchemy_interface.md).

### Quick Example

from doctable import DocTable2
class Documents(DocTable2):





## DocTable (Original) Class

This package provides a thin layer over the sqlite package specifically for working with single tables of data, as is often the case with many basic text analysis applications. Somewhere between a spreadsheet and full-fledged database server, this package allows for a very simple interface for storing, updating, and retrieving data. It transparently handles picklable python objects that can be stored as sqlite blob types, so you can treat python objects like any other retrievable database type.

The package consists of a single class called DocTable, a base class with useful read/write/update interface methods. This example (found in example_advanced.ipynb) shows the NewsGroups DocTable, where I have created columns file_id, category, raw_text, subject, author, and tokenized_text. Notice that tokenized_text has been assigned the "blob" type, which DocTable will automatically convert to and from Python objects automatically.


```
from doctable import DocTable

class NewsGroups(DocTable):
    def __init__(self, fname):
        '''
            DocTable class.
            Inputs:
                fname: fname is the name of the new sqlite database that will be used for instances of class.
        '''
        tabname = 'newsgroups'
        super().__init__(
            fname=fname, 
            tabname=tabname, 
            colschema='id integer primary key autoincrement, file_id int, category string, \
                raw_text string, subject string, author string, tokenized_text blob, UNIQUE(file_id)',
        )
        
        # create indices on file_id and category
        self.query("create index if not exists idx1 on "+tabname+"(file_id)")
        self.query("create index if not exists idx2 on "+tabname+"(category)")


```

See examples example_simple.ipynb and example_advanced.ipynb for demonstration of how to use this library.


NOTE: Right now I haven't included any text analysis-specific features. It just seems to be convenient for my text-based projects so far.



