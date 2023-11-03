# `doctable` Python Package

### Doctable is getting a new interface!

I recently updated doctable with an entirely new API to improve on some of the limitations of the previous interface and better match the new [Sqlalchemy 2.0](https://www.sqlalchemy.org/) interface. Inspired by the [attrs project](https://www.attrs.org/en/stable/names.html), I used different names for functions and classes to make it clear that the interface has changed and open the possibility for backwards compatibility with upgraded internals in the future. I decided to create the new API from scratch as it would have been more difficult to start from the old interface and improve incrementally, and I think the new interface works significantly better for the kinds of applications I have been using doctable for anyways. For now, stick to installing from the legacy repository when using sqlalchemy <= 1.4, and the master repository for sqlalchemy >= 2.0.

---

### Installation

From [Python Package Index](https://pypi.org/project/doctable/): `pip install doctable`

For sqlalchemy >= 2.0: `pip install --upgrade git+https://github.com/devincornell/doctable.git@master`

For sqlalchemy <= 1.4: `pip install --upgrade git+https://github.com/devincornell/doctable.git@legacy`




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
