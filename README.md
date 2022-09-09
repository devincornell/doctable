

# DocTable Python Package

Document database interface for text analysis.

See the [doctable website](https://devinjcornell.com/doctable/) for documentation and examples.

Created by [Devin J. Cornell](https://devinjcornell.com).

# Major Version Changes

### Version 0.9.5

+ Revamped schema decorator to default unretrieved column data to an empty value so that an exception can be raised when the user attempts to access it. When specifying columns in select queries, previously the user had to x.

Previously, when selecting specific columns
+ Switched from using EmptyValue() instances to a MISSING_VALUE object.

### Version 0.9.4

+ 


### Thanks

The setup of this package was created following [this guide](https://packaging.python.org/tutorials/packaging-projects/).
