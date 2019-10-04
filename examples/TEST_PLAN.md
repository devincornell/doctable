
** Test Plan For DocTable2 **

0. schema construction
    * test table creation with all types
    * test table loading with same schema
    * test table loading with different schema

1. simple insert
    * needs to insert main column first (so as to check constraints etc)
    * then insert special col data
    * check that both were inserted

2. simple select
    * try out select
    * try out select_iter
    * make sure the correct data is returned
    * can simply compare input to output

3. simple delete
    * try deleting main row and the subdoc rows should be gone

4. simple update
    * try updating main col with different subdoc info
    * all subdoc info should be replaced