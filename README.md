

# DocTable Python Package for SQAlchemy <= 1.4

Document database interface for text analysis.

See the [doctable website](https://devinjcornell.com/doctable/) for documentation and examples.

Created by [Devin J. Cornell](https://devinjcornell.com).

# Major Version Changes


### Version 1.0

+ Set to use string-based type hints to support Python version 3.9 and above.
+ Set sqlalchemy version requirement to <=1.4. Sqlalchemy v2.0+ will be supported in the next version.
+ This is the last release that supports sqlalchemy <= v1.4.

### Version 0.9.5

+ Revamped schema decorator to default unretrieved column data to an empty value so that an exception can be raised when the user attempts to access it. When specifying columns in select queries, previously the user had to manually detect an EmptyValue object.

+ removed ability to use `_doctable_args_` and `_engine_kwargs_` static properties. Instead, user should just overload `__init__`. I don't think many projects used that anyways, and this fits better with the [Zen of Python](https://peps.python.org/pep-0020/): "There should be one-- and preferably only one --obvious way to do it."

Previously, when selecting specific columns
+ Switched from using EmptyValue() instances to a MISSING_VALUE object instance.

### Thanks

The setup of this package was created following [this guide](https://packaging.python.org/tutorials/packaging-projects/).
