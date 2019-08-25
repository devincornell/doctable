

# DocTable Package

Object-based database access for text analysis.

This package provides a thin layer over the sqlite package specifically for working with single tables of data, as is often the case with many basic text analysis applications. Somewhere between a spreadsheet and full-fledged database server, this package allows for a very simple interface for storing, updating, and retrieving data. It transparently handles picklable python objects that can be stored as sqlite blob types, so you can treat python objects like any other retrievable database type.

## Robust Data Access Interface

The DocTable package provides several different ways of

* SELECT
    * one row at a time (more overhead, memory efficient)
    * entire dataset at once (low overhead, memory intensive)
* INSERT
    * single item
    * insert many from stream/iterable
    * insert many from memory
* UPDATE
* DELETE



## Example

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



