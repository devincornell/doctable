# Example: Multiple Tables
In this example, I show how doctable can be used with multiple relational tables to perform queries which automatically merge different aspects of your dataset when you use `.select()`. By integrating these relations into the schema, your database can automatically maintain consistency between tables by deleting irrelevant elements when their relations disappear. There are two important features of any multi-table schema using doctable:

(1) Set the foreign_keys=True in the DocTable or ConnectEngine constructor. It is enabled by default. Otherwise sqlalchemy will not enable.

(2) Use the "foreignkey" column type to set the constraint, probably with the onupdate and ondelete keywords specifiied.

I will show two examples here: many-to-many relations, and many-to-one relations.



```python
import datetime
import dataclasses
import tempfile
import sys
sys.path.append('..')
import doctable
tmp = tempfile.TemporaryDirectory()
```

## Many-to-Many Relationships

The premise is that we have an imaginary API where we can get newly released books along with the libraries they are associted with (although they man, in some cases, not have library information). We want to keep track of the set of books with unique titles, and have book information exist on its own (i.e. we can insert book information if it does not have library information). We would also like to keep track of the libraries they belong to. We need this schema to be fast for selection, but it can be slow for insertion.

Primary accesses methods:

+ insert a book
+ query books by year of publication
+ insert a single library and associated books
+ query books associated with libraries in certain zips

In this example, we are going to use two tables with a many-to-many relationships and a table to handle relationships between them (required for a many-to-many relationship):
    
+ *`BookTable`*: keeps title and publication year of each book. Should exist independently of LibraryTable, because we may not want to use LibraryTable at all.
+ *`LibraryTable`*: keeps name of library, makes it easy to query by Library.
+ *`BookLibraryRelationsTable`*: keeps track of relationships between BookTable and LibraryTable.

First we define the `BookTable` table. Because we are primarily interested in books, we will create a separate `Book` object for working with them.


```python
@doctable.schema(frozen=True, eq=True)
class Book:
    __slots__ = []
    _id: int = doctable.IDCol()
    isbn: str = doctable.Col(unique=True)
    title: str = doctable.Col()
    year: int = doctable.Col()
    author: str = doctable.Col()
    date_updated: datetime.datetime = doctable.UpdatedCol()

class BookTable(doctable.DocTable):
    _tabname_ = 'books'
    _schema_ = Book
    _indices_ = [doctable.Index('isbn_index', 'isbn')]
    
book_table = BookTable(target=f'{tmp.name}/1.db', new_db=True)
```

We are not planning to work with author data outside of the schema definition, so we include it as part of the table definition.


```python
@doctable.schema(frozen=True, eq=True)
class Library:
    __slots__ = []
    _id: int = doctable.IDCol()
    name: str = doctable.Col()
    zip: int = doctable.Col()

class LibraryTable(doctable.DocTable):
    _tabname_ = 'libraries'
    _schema_ = Library    
    _constraints_ = [doctable.Constraint('unique', 'name', 'zip')]
    

library_table = LibraryTable(engine=book_table.engine)
```


```python
class BookLibraryRelationsTable(doctable.DocTable):
    '''Link between books and libraries.'''
    _tabname_ = 'book_library_relations'
    
    @doctable.schema
    class _schema_:
        __slots__ = []
        _id: int = doctable.IDCol()
        book_isbn: int = doctable.Col(nullable=False)
        library_id: int = doctable.Col(nullable=False)
    
    _constraints_ = (
        doctable.Constraint('foreignkey', ('book_isbn',), ('books.isbn',)),
        doctable.Constraint('foreignkey', ('library_id',), ('libraries._id',)),
        doctable.Constraint('unique', 'book_isbn', 'library_id'),
    )

relations_table = BookLibraryRelationsTable(engine=book_table.engine)
relations_table.list_tables()
```




    ['book_library_relations', 'books', 'libraries']



Now we create some random books that are not at libraries and add them into our database.


```python
newly_published_books = [
    Book(isbn='A', title='A', year=2020, author='Pierre Bourdieu'),
    Book(isbn='E', title='E', year=2018, author='Jean-Luc Picard'),
]

for book in newly_published_books:
    print(book)
```

    Book(isbn='A', title='A', year=2020, author='Pierre Bourdieu')
    Book(isbn='E', title='E', year=2018, author='Jean-Luc Picard')


Now we insert the list of books that were published. It works as expected.


```python
book_table.insert(newly_published_books, ifnotunique='replace')
book_table.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>_id</th>
      <th>isbn</th>
      <th>title</th>
      <th>year</th>
      <th>author</th>
      <th>date_updated</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>A</td>
      <td>A</td>
      <td>2020</td>
      <td>Pierre Bourdieu</td>
      <td>2022-07-26 21:30:30.364805</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>E</td>
      <td>E</td>
      <td>2018</td>
      <td>Jean-Luc Picard</td>
      <td>2022-07-26 21:30:30.364812</td>
    </tr>
  </tbody>
</table>
</div>



And now lets add a bunch of books that are associated with library objects.


```python
new_library_books = {
    Library(name='Library1', zip=12345): [
        Book(isbn='A', title='A', year=2020, author='Pierre Bourdieu'),
        Book(isbn='B', title='B', year=2020, author='Pierre Bourdieu'),
    ],
    Library(name='Library2', zip=12345): [
        Book(isbn='A', title='A', year=2020, author='Devin Cornell'),
        Book(isbn='C', title='C', year=2021, author='Jean-Luc Picard'),
    ],
    Library(name='Library3', zip=67890): [
        Book(isbn='A', title='A', year=2020, author='Pierre Bourdieu'),
        Book(isbn='B', title='B', year=2020, author='Jean-Luc Picard'),
        Book(isbn='D', title='D', year=2019, author='Devin Cornell'),
    ],
}

for library, books in new_library_books.items():
    r = library_table.insert(library, ifnotunique='ignore')
    book_table.insert(books, ifnotunique='replace')
    relations_table.insert([{'book_isbn':b.isbn, 'library_id': r.lastrowid} for b in books], ifnotunique='ignore')
```


```python
book_table.select_df()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>_id</th>
      <th>isbn</th>
      <th>title</th>
      <th>year</th>
      <th>author</th>
      <th>date_updated</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>E</td>
      <td>E</td>
      <td>2018</td>
      <td>Jean-Luc Picard</td>
      <td>2022-07-26 21:30:30.364812</td>
    </tr>
    <tr>
      <th>1</th>
      <td>6</td>
      <td>C</td>
      <td>C</td>
      <td>2021</td>
      <td>Jean-Luc Picard</td>
      <td>2022-07-26 21:30:30.482867</td>
    </tr>
    <tr>
      <th>2</th>
      <td>7</td>
      <td>A</td>
      <td>A</td>
      <td>2020</td>
      <td>Pierre Bourdieu</td>
      <td>2022-07-26 21:30:30.494686</td>
    </tr>
    <tr>
      <th>3</th>
      <td>8</td>
      <td>B</td>
      <td>B</td>
      <td>2020</td>
      <td>Jean-Luc Picard</td>
      <td>2022-07-26 21:30:30.494692</td>
    </tr>
    <tr>
      <th>4</th>
      <td>9</td>
      <td>D</td>
      <td>D</td>
      <td>2019</td>
      <td>Devin Cornell</td>
      <td>2022-07-26 21:30:30.494694</td>
    </tr>
  </tbody>
</table>
</div>




```python
library_table.select_df()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>_id</th>
      <th>name</th>
      <th>zip</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Library1</td>
      <td>12345</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Library2</td>
      <td>12345</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Library3</td>
      <td>67890</td>
    </tr>
  </tbody>
</table>
</div>




```python
relations_table.select_df()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>_id</th>
      <th>book_isbn</th>
      <th>library_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>A</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>B</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>A</td>
      <td>2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>C</td>
      <td>2</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>A</td>
      <td>3</td>
    </tr>
    <tr>
      <th>5</th>
      <td>6</td>
      <td>B</td>
      <td>3</td>
    </tr>
    <tr>
      <th>6</th>
      <td>7</td>
      <td>D</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>



### Select Queries That Join Tables

Similar to sqlalchemy, `DocTable` joins are doen simply by replacing the where conditional. While not technically nessecary, typically you will be joining tables on foreign key columns because it is much faster.


```python
bt, lt, rt = book_table, library_table, relations_table
```

For the first example, say we want to get the isbn numbers of books associated with each library in zip code 12345. We implement the join using a simple conditional  equating the associated keys in each table. Our database schema already knows that the foreign keys are in place, so this expression will give us the join we want.


```python
lt.select([lt['name'], rt['book_isbn']], where=(lt['_id']==rt['library_id']) & (lt['zip']==12345), as_dataclass=False)
```




    [('Library1', 'A'), ('Library1', 'B'), ('Library2', 'A'), ('Library2', 'C')]



Now say we want to characterize each library according to the age distribution of it's books. We use two conditionals for the join: one connecting library table to relations table, and another connecting relations table to books table. We also include the condition to get only libraries associated with the given zip.


```python
conditions = (bt['isbn']==rt['book_isbn']) & (rt['library_id']==lt['_id']) & (lt['zip']==12345)
bt.select([bt['title'], bt['year'], lt['name']], where=conditions, as_dataclass=False)
```




    [('C', 2021, 'Library2'),
     ('A', 2020, 'Library1'),
     ('A', 2020, 'Library2'),
     ('B', 2020, 'Library1')]



Alternatively we can use the `.join` method of doctable (although I recommend just using select statements).


```python
jt = lt.join(rt, (lt['zip']==12345) & (lt['_id']==rt['library_id']), isouter=False)
bt.select(where=bt['isbn']==jt.c['book_library_relations_book_isbn'], as_dataclass=True)
bt.select([bt['title'], jt.c['book_library_relations_library_id']], where=bt['isbn']==jt.c['book_library_relations_book_isbn'], as_dataclass=False)
bt.select([bt['title'], jt.c['libraries_name']], where=bt['isbn']==jt.c['book_library_relations_book_isbn'], as_dataclass=False, limit=3)
```




    [('C', 'Library1'), ('C', 'Library2'), ('C', 'Library3')]



## Many-to-One Relationships
Now we create an author class and table to demonstrate a many-to-one relationship.


```python
@doctable.schema(frozen=True, eq=True)
class Author:
    __slots__ = []
    #_id: int = doctable.IDCol()
    name: str = doctable.Col(primary_key=True, unique=True)
    age: int = doctable.Col()

class AuthorTable(doctable.DocTable):
    _tabname_ = 'authors'
    _schema_ = Author  
    _constraints_ = [doctable.Constraint('foreignkey', ('name',), ('books.author',))]

#book_table_auth = BookTable(target=f'{tmp.name}/16.db', new_db=True)
#author_table = AuthorTable(engine=book_table_auth.engine)
author_table = AuthorTable(engine=book_table.engine)
```


```python
author_table.delete()
author_table.insert([
    Author(name='Devin Cornell', age=30),
    Author(name='Pierre Bourdieu', age=99),
    Author(name='Jean-Luc Picard', age=1000),
])
author_table.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Devin Cornell</td>
      <td>30</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Pierre Bourdieu</td>
      <td>99</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Jean-Luc Picard</td>
      <td>1000</td>
    </tr>
  </tbody>
</table>
</div>




```python
book_table.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>_id</th>
      <th>isbn</th>
      <th>title</th>
      <th>year</th>
      <th>author</th>
      <th>date_updated</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>E</td>
      <td>E</td>
      <td>2018</td>
      <td>Jean-Luc Picard</td>
      <td>2022-07-26 21:30:30.364812</td>
    </tr>
    <tr>
      <th>1</th>
      <td>6</td>
      <td>C</td>
      <td>C</td>
      <td>2021</td>
      <td>Jean-Luc Picard</td>
      <td>2022-07-26 21:30:30.482867</td>
    </tr>
    <tr>
      <th>2</th>
      <td>7</td>
      <td>A</td>
      <td>A</td>
      <td>2020</td>
      <td>Pierre Bourdieu</td>
      <td>2022-07-26 21:30:30.494686</td>
    </tr>
    <tr>
      <th>3</th>
      <td>8</td>
      <td>B</td>
      <td>B</td>
      <td>2020</td>
      <td>Jean-Luc Picard</td>
      <td>2022-07-26 21:30:30.494692</td>
    </tr>
    <tr>
      <th>4</th>
      <td>9</td>
      <td>D</td>
      <td>D</td>
      <td>2019</td>
      <td>Devin Cornell</td>
      <td>2022-07-26 21:30:30.494694</td>
    </tr>
  </tbody>
</table>
</div>




```python
columns = [book_table['year'], author_table['age'], author_table['name']]
where = (book_table['author']==author_table['name']) & (book_table['author'] > 30)
book_table.select_df(columns, where=where)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>age</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2018</td>
      <td>1000</td>
      <td>Jean-Luc Picard</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2021</td>
      <td>1000</td>
      <td>Jean-Luc Picard</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2020</td>
      <td>99</td>
      <td>Pierre Bourdieu</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2020</td>
      <td>1000</td>
      <td>Jean-Luc Picard</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2019</td>
      <td>30</td>
      <td>Devin Cornell</td>
    </tr>
  </tbody>
</table>
</div>


