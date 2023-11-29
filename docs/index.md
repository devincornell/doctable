
![doctable diagram](https://storage.googleapis.com/public_data_09324832787/website_diagram_v5.svg)

`doctable` is a Python package for manipulating SQL databases through an object-oriented interface without the overhead of object-relational mapping. It is built on top of the [Sqlalchemy](https://www.sqlalchemy.org/) core interface, and takes advantage of [dataclasses](https://docs.python.org/3/library/dataclasses.html) to define database schemas.

`doctable` also enables the high-performance storage of binary files (think ML models), parse trees, and compressed text files.

Created by [Devin J. Cornell](https://devinjcornell.com).

### Doctable has a new interface!

The package has been updated with an entirely new API to improve on previous limitations and better match the [Sqlalchemy 2.0](https://www.sqlalchemy.org/) interface. Inspired by the [attrs project](https://www.attrs.org/en/stable/names.html), I used different names for functions and classes to make it clear that the interface has changed and open the possibility for backwards compatibility with upgraded internals in the future. 

For now, install version 1.0 when using sqlalchemy <= 1.4 and version 2.0 when using sqlalchemy >= 2.0. See the installation page for more.

