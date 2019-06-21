import email
from example_helper import get_sklearn_newsgroups # for this example

from doctable import DocTable # this will be the table object we use to interact with our database.

ddf = get_sklearn_newsgroups()
print(ddf.shape)
ddf.head(3)
