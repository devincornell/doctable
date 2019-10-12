

# DocTable Package for Python

Object-based database access specifically intended for text analysis applications.

The package makes it easy to create a new database tables with simple schemas; a common task in many text analysis projects. The package consists primarily of two classes: the original [**DocTable**](https://devincornell.github.io/doctable/doctable.DocTable.html), built directly as a thin interface to the sqlite3 package, and [**DocTable2**](https://devincornell.github.io/doctable/doctable.DocTable2.html), the successor which is implemented using SQLAlchemy.

The typical way to use this package is to create new classes which inherit from DocTable2 or DocTable. These classes can manage schema info and allow users to add application-specific member functions for convenient access to the underlying databases.

See the documentation here: [DocTable2 Class Documentation](https://devincornell.github.io/doctable/doctable.DocTable2.html), [DocTable Class Documentation](https://devincornell.github.io/doctable/doctable.DocTable.html)

## DocTable2 Class

[**DocTable2**](https://devincornell.github.io/doctable/doctable.DocTable2.html) is built on [SQLAlchemy Core](https://docs.sqlalchemy.org/en/13/core/), a flexible object-oriented interface to many mainstream DB engines. DocTable2 is inspired by the object-based interface of SQLAlchemy, but makes it easier to access SQLAlchemy features without importing a large number of python objects. The interface requires much less user code compared to SQLAlchemy, taking cues from the original Doctable class.

### Examples
Most of the documentation for DocTable2 is provided via the examples. Here is a list of example notebooks and scripts:

- [DocTable2 Function Documentation](docs/doctable.DocTable2.html)
- [DocTable2 Basic Examples](docs/dt2_basics.md)
- [Insert/Delete Examples](docs/dt2_insert_delete.md)
- [Select Examples](docs/dt2_select.md)
- [Update Examples](docs/dt2_update.md)
- [Schema Examples](examples/dt2_schema.py)
- [Special Column Type Examples](docs/dt2_specialtypes.md)

### Quick Example

The initialization of a doctable requires a schema, as shown in this example. See the [DocTable2 Basics Document](docs/dt2_basics.ipynb) for more.

    ```python

    schema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('name','string', dict(nullable=False)),
        ('age','integer'),
    )
    db = dt.DocTable2(schema, fname='test.db')

    ```
    
After creating the instance, the database and table have been created according to the desired schema. Now, just to add a few items:

    ```python
    
    N = 5
    for i in range(N):
        age = random.random() # number in [0,1]
        row = {'name':'user_'+str(i), 'age':age}
        db.insert(row)
    ```

Now we use the ```.select()``` method to view the contents of the database:

    ```python
    db.select()
    ```
The output will yield this:

```
[(1, 'user_0', 0.4161851979243477),
 (2, 'user_1', 0.37148559537119163),
 (3, 'user_2', 0.9389122192656695),
 (4, 'user_3', 0.6709306663312412),
 (5, 'user_4', 0.4574398725307163)]
```
    
Read the [basic introduction](docs/dt2_basics.ipynb) or other examples to see more!

    
### Special Data Types

In addition to regular schema mappings, DocTable2 provides custom data types for token lists and lists of token lists (think tokenized sentences). See the [Special Type Examples](docs/dt2_specialtypes.ipynb) for more information.



## Original DocTable Class

[**DocTable**](https://devincornell.github.io/doctable/doctable.DocTable.html) provides a thin layer over the sqlite package specifically for working with single tables of data, as is often the case with many basic text analysis applications. Somewhere between a spreadsheet and full-fledged database server, this package allows for a very simple interface for storing, updating, and retrieving data. It transparently handles picklable python objects that can be stored as sqlite blob types, so you can treat python objects like any other retrievable database type.

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

# Thanks

The setup of this package was created following [this guide](https://packaging.python.org/tutorials/packaging-projects/).
