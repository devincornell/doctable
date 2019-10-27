import os
import sqlite3
import _pickle as pickle
import pandas as pd

##### DOCUMENT INTERFACE FOR WORKING WITH TEXT DATA #####

class DocTable:
    '''
        This is a base class for working with text documents. 
        It is to be inhereted by a class actually defining the table schema for documents.
    '''
    
    def __init__(self,
                 colschema=None, 
                 fname='doctable.db',  
                 tabname='documents', 
                 constraints=tuple(), 
                 verbose=False, 
                 persistent_conn=True, 
                 make_new_db=True, 
                 check_schema=True, 
                ):
        '''
        Args:
            fname (str): filename of database
            tabname (str): name of sqlite table to manipulate.
            colschema (tuple of 2-tuples): list of colname, coltype columns
            constraints (tuple of str): constraints to put on columns
            verbose (bool): print querys before executing
            persistent_conn (bool): keep a persistent sqlite3 connection to 
                the db.
            new_db (bool): create a new database file if one does not already 
                exist. Prevents creation of new db if filename is mis-specified.
        '''
        
        if fname!=':memory:' and not os.path.exists(fname) and not make_new_db:
            raise FileNotFoundError('The {} database file does not exist and '
                'make_new_db is set to False.'.format(fname))
        
        if fname!=':memory:' and not os.path.exists(fname) and colschema is None:
            raise ValueError('The database file does not exist already and a '
                'a colschema was not provided. Need to provide a colschema to '
                'create a new database.')
        
        if check_schema and colschema is None:
            raise ValueError('check_schema was set to true but colschema was '
                'not provided.')
        
        self.fname = fname
        self.tabname = tabname
        self.colschema = colschema
        self.constraints = constraints
        self.verbose = verbose
        self.conn = None
        
        self._try_create_table()
        
        self.schema = self._get_schema()
        self.columns = list(self.schema['name'])
        
        if check_schema and fname != ':memory:':
            self._check_schema()
        
        if persistent_conn:
            self.conn = sqlite3.connect(fname)
        
        self.isblob = {name:d['type'].lower()=='blob' for name,d in self.schema.iterrows()}
        
        
    
    def _try_create_table(self,):
        
        args = (self.tabname, ', '.join(self.colschema + self.constraints))
        return self.query('CREATE TABLE IF NOT EXISTS {} ({})'.format(*args))
        
    def _check_schema(self,):
        '''
            Compares actual table schema to user-provided schema.
        '''
        for colinfo in self.colschema:
            colinfo = colinfo.split()
            cname, ctype = colinfo[0], colinfo[1]
            if cname not in self.columns:
                estr = ('colschema entry "{}" is not found in '
                        'existing table cols: {}')
                raise ValueError(estr.format(cname, self.columns))
                
            elif ctype != self.schema.loc[cname,'type']:
                exist_type = self.schema.loc[cname,'type']
                estr = ('provided "{}" column type "{}" does not match '
                        'existing data schema type "{}".')
                raise ValueError(estr.format(cname, ctype, exist_type))
            else:
                pass
    
    def _get_schema(self):
        '''
            Sets schema from table, parsing out variable names and types.
        '''
        qstr = 'PRAGMA table_Info("{}")'.format(self.tabname,)
        result = tuple(self.query(qstr))
        
        cols = ['cid', 'name', 'type', 'notnull', 'dflt_value','pk']
        schema_df = pd.DataFrame(index=range(len(result)), columns=cols)
        
        for i,row in enumerate(result):
            schema_df.iloc[i] = row
            
        schema_df = schema_df.set_index('name',drop=False)
            
        return schema_df

    
    def _get_existing_tables(self):
        '''
            Gets list of existing tables in the db.
        '''
        res = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        existcols = [col[0] for col in res]
        return existcols
    
    
    def __del__(self):
        '''
            Closes connection upon deletion.
        '''
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
        
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
        if self.conn is not None:
            return self.conn.commit()
        # do nothing otherwise; change to exception later?
    
    
    def query(self, qstr, payload=None, many=False, verbose=False):
        '''
            Executes raw query using database connection.
            
            Output: sqlite query conn.execute() output.
        '''
        if self.verbose or verbose: print(qstr)
        
        # make a new connection and cursor
        if self.conn is None:
            with sqlite3.connect(self.fname) as conn:
                cursor = conn.cursor()
                return self._query_exec(cursor, qstr, payload, many)
        
        # use instance connection and make new cursor
        else:
            cursor = self.conn.cursor()
            return self._query_exec(cursor, qstr, payload, many)
        
    @staticmethod
    def _query_exec(cursor, qstr, payload, many):
        if payload is None:
            return cursor.execute(qstr)
        else:
            if not many:
                return cursor.execute(qstr,payload)
            else:
                return cursor.executemany(qstr,payload)
    
        
    def _pickle_values(self, cols, values, serialize=True):
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
            raise ValueError('Not all submitted columns are in database.')
        
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
    
    
    def add(self, datadict, ifnotunique=None, **queryargs):
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
        payload = self._pickle_values(cols, values, serialize=True)
        n = len(cols)
        replacecode = ' OR ' + ifnotunique if ifnotunique is not None else ''
        
        qstr = 'INSERT'+replacecode+' INTO ' + self.tabname + '('+','.join(cols)+') VALUES ('+','.join(['?']*n)+')'
        return self.query(qstr, payload, **queryargs)
        
    def addmany(self, data, keys=None, ifnotunique=None, **queryargs):
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
            payload = [self._pickle_values(cols, values, serialize=True) for values in data]
        else:
            payload = data
        
        replacecode = ' OR ' + ifnotunique if ifnotunique is not None else ''
        qstr = 'INSERT'+replacecode+' INTO ' + self.tabname + '('+','.join(cols)+') VALUES ('+','.join(['?']*n)+')'
        
        return self.query(qstr, payload, many=True, **queryargs)
    
    def delete(self, where=None, **queryargs):
        '''
            Deletes all rows matching the where criteria.
                
            Inputs:
                where: if "*" is specified, will drop all rows. Otherwise
                    is fed directly into the query statement.
            
            Output:
                query response
        '''
        qstr = 'DELETE FROM '+ self.tabname
        if where is not None:
            qstr += ' WHERE ' + where
            
        return self.query(qstr, **queryargs)
        
    
    def update(self, values, where, **queryargs):
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

        pickled_values = self._pickle_values(cols, vals, serialize=True)
        return self.query(qstr,pickled_values, **queryargs)
    
            
    def get(self, sel=None, where=None, orderby=None, limit=None, table=None, verbose=False, asdict=True, **queryargs):
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
                kwargs: to be sent to self.query().
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
            for result in self.query(qstr, **queryargs):
                yield {
                    col:val for col,val in zip(usecols,self._pickle_values(usecols,result,serialize=False))
                }
        else:
            for result in self.query(qstr, **queryargs):
                yield self._pickle_values(usecols,result,serialize=False)
        
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