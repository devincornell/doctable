import sqlite3
import pickle
import pandas as pd

##### DOCUMENT INTERFACE FOR WORKING WITH TEXT DATA #####

class DocTable:
    '''
        This is a base class for working with text documents. 
        It is to be inhereted by a class actually defining the table schema for documents.
    '''
    
    def __init__(self,
                 fname='documents.db', 
                 conn=None,
                 tabname='documents', 
                 colschema='num integer, doc blob',
                 verbose=False,
                ):
        
        self.colschema = colschema
        self.tabname = tabname
        self.verbose = verbose
        
        #self.doccol = columns.split(',')[-1].strip().split(' ')[0].strip()
        self.conn = sqlite3.connect(fname) if conn is None else conn        
        
        # make new table if needed, ensure schema is same
        res = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        existcols = [col[0] for col in res]
        if tabname not in existcols:
            self.query("create table "+self.tabname+"("+self.colschema+")")
        else:
            spec_schema = [col.strip().split() for col in colschema.split(',')]
            spec_schema = [(col[0],col[1]) for col in spec_schema if not '(' in ''.join(col)]
            
            if spec_schema != self.get_schema():
                s_str = 'old: {}, new: {}'.format(spec_schema, self.get_schema())
                raise Exception('The specified schema does not match existing table!', s_str)
            
        self.schema = self.get_schema()
        self.isblob = {name:dtype=='blob' for name,dtype in self.schema}
        self.columns = [s[0] for s in self.schema]
        
    
    def get_schema(self):
        '''
            Gets schema for table, parses out variable names and types.
        '''
        qstr = 'PRAGMA table_Info("{}")'.format(self.tabname,)
        result = self.query(qstr)
        
        # cn[1] is column name and cn[2] is column data type
        # this can be compared with a parsing of the originally offerend colschema
        schema = [(cn[1],cn[2]) for cn in result]
        return schema
    
    def __del__(self):
        '''
            Closes connection upon deletion.
        '''
        self.conn.commit()
        
    def __str__(self):
        '''
            Outputs string specifying number of documents in the table.
            
            Output: string of doc info
        '''
        info = ''
        
        ct = self.query('SELECT Count(*) FROM '+self.tabname).__next__()[0]
        info += '<Documents ct: ' + str(ct) + '>'
        
        return info
    
    def commit(self):
        '''
            Commits database changes to file.
        '''
        return self.conn.commit()
    
    
    def query(self, qstr, payload=None, many=False, verbose=False):
        '''
            Executes raw query using database connection.
            
            Output: sqlite query conn.execute() output.
        '''
        if self.verbose or verbose: print(qstr)
            
        cursor = self.conn.cursor()
        
        if payload is None:
            return cursor.execute(qstr)
        else:
            if not many:
                return cursor.execute(qstr,payload)
            else:
                return cursor.executemany(qstr,payload)
    
        
    def pickle_values(self, cols, values, serialize=True):
        '''
            Converts blob type columns into pickled blobs. 
                Also error-checks submitted columns.
            
            Inputs:
                cols: list of columns associated with each value
                values: list or tuple of values to potentially convert
            
            Output:
                list of values with python objects pickled into blobs
        '''
        if not all([c in self.columns for c in cols]):
            raise Exception('Not all submitted columns are in database.')
        
        out_values = list()
        for colname,val in zip(cols,values):
            if self.isblob[colname]:
                if serialize:
                    out_values.append( pickle.dumps(val) )
                else:
                    if val is not None:
                        out_values.append( pickle.loads(val) )
                    else:
                        out_values.append( None )
            else:
                out_values.append(val)
        return out_values
    
    
    def add(self, datadict, ifnotunique=None):
        '''
            Adds a single entry where each column is identified by a key-value pair. 
                Will automatically convert python types to sqlite storage blobs using pickle.
            
            Inputs:
                datadict: dictionary of column name -> value mappings
                ifnotunique: choose what happens when an existing entry matches
                    any UNIQUE criteria specified in the schema.
                    Choose from ('REPLACE', 'IGNORE').
            Output:
                query response
        '''
        data = list(datadict.items())
        cols = [c for c,v in data]
        values = [v for c,v in data]
        #payload = [datadict[c] if not (c in self.isblob.keys() and self.isblob[c]) else pickle.dumps(datadict[c]) for c in cols]
        payload = self.pickle_values(cols, values, serialize=True)
        n = len(cols)
        replacecode = ' OR ' + ifnotunique if ifnotunique is not None else ''
        
        qstr = 'INSERT'+replacecode+' INTO ' + self.tabname + '('+','.join(cols)+') VALUES ('+','.join(['?']*n)+')'
        return self.query(qstr, payload)
        
    def addmany(self, data, keys=None, ifnotunique=None):
        '''
            Adds multiple entries to the database, where column names are specified by "keys".
                If "keys" is not specified, will use all columns (including autoincrement columns).
                Will automatically convert python types to sqlite storage blobs using pickle.
                
            Inputs:
                data: lists of tuples representing data for each row
                keys: column names corresponding to each tuple entry
                ifnotunique: choose what happens when an existing entry matches
                    any UNIQUE criteria specified in the schema.
                    Choose from ('REPLACE', 'IGNORE').
            Output:
                sqlite executemany query response
        '''
        # use all columns if keys is not specified
        cols = list(keys) if keys is not None else self.columns
        n = len(cols)
        
        
        if sum(self.isblob.values()) > 0:
            # need to convert some python objects to blobs for storage
            #payload = ([d[i] if not self.isblob[c] else pickle.dumps(d[i]) for i,c in enumerate(cols)] for d in data)
            payload = [self.pickle_values(cols, values, serialize=True) for values in data]
        else:
            payload = data
        
        replacecode = ' OR ' + ifnotunique if ifnotunique is not None else ''
        qstr = 'INSERT'+replacecode+' INTO ' + self.tabname + '('+','.join(cols)+') VALUES ('+','.join(['?']*n)+')'
        
        return self.query(qstr, payload, many=True)
    
    def delete(self, where):
        '''
            Deletes all rows matching the where criteria.
                
            Inputs:
                where: if "*" is specified, will drop all rows. Otherwise
                    is fed directly into the query statement.
            
            Output:
                query response
        '''
        qstr = 'DELETE FROM '+ self.tabname
        if where == '*':
            qstr += ' WHERE ' + where
            
        return self.query(qstr)
        
    
    def update(self, values, where):
        '''
            Updates rows matching the "where" string with specified values.
                
            Inputs:
                values: dictionary of field->values. all rows which meet the where criteria 
                    will have these values assigned
                where: literal SQLite "where" string corresponding to column criteria for 
                    value replacement.
                    The value "*" will match all rows by omitting WHERE statement.
            Output:
                query response
        '''
        valuelist = list(values.items())
        vals = [v for k,v in valuelist]
        cols = [k for k,v in valuelist]
        # UPDATE tasks SET priority = ?, begin_date = ?, end_date = ? WHERE id = ?
        qstr =  'UPDATE '+self.tabname+' SET ' + ', '.join([c+' = ?' for c in cols])
        if where != '*':
            qstr += ' WHERE ' + where

        pickled_values = self.pickle_values(cols, vals, serialize=True)
        return self.query(qstr,pickled_values)
    
            
    def get(self, sel=None, where=None, orderby=None, limit=None, table=None, verbose=False, asdict=True):
        '''
            Query rows from database as generator.
                
            Inputs:
                sel: list of fields to retrieve with the query
                where: literal SQLite "where" string corresponding to criteria for 
                    value replacement.
                orderby: literal sqlite order by command value. Can be "column_1 ASC",
                    or order by multiple columns using, for instance, "column_1 ASC, column_2 DESC"
                limit: number of rows to retrieve before stopping query. Can be used for quick testing.
                table: table name to retrieve for. Default is object table name, but can query from 
                    others here.
                verbose: True/False flag indicating whether or not output should appear.
                asdict: True/False flag indicating whether rows should be returned as 
                    lists (False) or as dicts with field names (True & default).
        '''
                
        tabname = table if table is not None else self.tabname
        whereclause = ' WHERE '+where if where is not None else ''
        orderbyclause = (' ORDER BY '+orderby) if orderby is not None else ''
        limitclause = ' LIMIT ' + str(limit) if limit is not None else ''
        
        if sel is None:
            usecols = self.columns
        else:
            usecols = sel
        
        n = len(usecols)
        
        qstr = 'select '+','.join(usecols)+' from '+tabname+whereclause+orderbyclause+limitclause
        if verbose: print(qstr)
        
        if asdict:
            for result in self.query(qstr):
                yield {
                    col:val for col,val in zip(usecols,self.pickle_values(usecols,result,serialize=False))
                }
        else:
            for result in self.query(qstr):
                yield self.pickle_values(usecols,result,serialize=False)
        
    def getdf(self, *args, **kwargs):
        '''
            Query rows from database, return as Pandas DataFrame.
                
            Inputs:
                See inputs for self.get().
        '''
        results = list(self.get(*args, **kwargs))
        if len(results) > 0:
            sel = list(results[0].keys())
        else:
            try:
                sel
            except NameError:
                sel = list()
        return pd.DataFrame(results, columns=sel)




        
        
