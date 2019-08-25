

# DocTable Package for Python

Object-based database access specifically intended for text analysis applications. The package makes it easy to create a new sqlite data table with simple schemas; a common task in many text analysis projects. The package consists primarily of two classes: the original DocTable, built directly as a thin interface to the sqlite3 package, and DocTable2, the successor which is implemented using SQLAlchemy.

The typical way to use this package is to create new classes which inherit from DocTable2 or DocTable. These classes can manage schema info and allow users to add application-specific member functions for convenient access to the underlying database. Custom member interfaces benefit from useful features in DocTable.

Generally these interfaces are intended to provide an object-oriented interface to a database which is designed to be in-synch with databases. If the schema of the object changes, it can be more difficult to access data in a database which was created using a different schema. As such, it can be helpful to version database interfaces with different schemas.

## DocTable2 Class

This class is built on SQLAlchemy, a flexible object-oriented interface to many mainstream DB engines. This class is inspired by the object-based interface of SQLAlchemy but makes it easier to access SQLAlchemy features without importing a large number of database objects. The interface requires much less user code compared to SQLAlchemy, taking cues from the original Doctable class.

The additional advantage of DocTable2 over the original DocTable is the transparent access to a multi-table schema based on DocTable's built-in custom data types. This additional feature makes it easy to store data of large size, specifically large Python objects, which would normally slow down queries to non-data columns.

* **bigblob column type**: This column type stores large pickled Python objects in a separate table from the primary table automatically created by DocTable. The .select_iter() method of DocTable2 will will perform a separate query for each row yield to minimize memory overhead and ensure the database does not queue the select query from that column. In contrast, the .select() method will perform one query to the bigblob table, collecting all python objects with a single query and automatically merge them with results from the primary document table.

* **subdoc column type**: This column type is for storing separate sub-document level token lists with one (document)-to-many (subdocs) relationships. This is primarily useful because of the frequent requirement to bootstrap text corpora at the sentence or paragraph (any sub-document) level - a useful feature for analyzing the sensitivity of a particular text analysis project to sub-document samples.

### Interface to SQLAlchemy



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



