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
        self.c = self.conn.cursor()
        self.schema = self.get_schema()
        
        # make new table if needed, ensure schema is same
        res = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        existcols = [col[0] for col in res]
        if tabname not in existcols:
            self.c.execute("create table "+self.tabname+"("+self.colschema+")")
        else:
            spec_schema = [col.strip().split() for col in colschema.split(',')]
            spec_schema = [(col[0],col[1]) for col in spec_schema if not '(' in ''.join(col)]
            
            if spec_schema != self.schema:
                s_str = 'old: {}, new: {}'.format(spec_schema, self.get_schema())
                raise Exception('The specified schema does not match existing table!', s_str)
            
        
        self.isblob = {name:dtype=='blob' for name,dtype in self.schema}
        self.columns = [s[0] for s in self.schema]
        
    
    def get_schema(self):
        qstr = 'PRAGMA table_Info("{}")'.format(self.tabname,)
        result = self.c.execute(qstr)
        
        # cn[1] is column name and cn[2] is column data type
        # this can be compared with a parsing of the originally offerend colschema
        schema = [(cn[1],cn[2]) for cn in result]
        return schema
    
    def __del__(self):
        self.conn.commit()
        
    def __str__(self):
        info = ''
        
        ct = self.c.execute('SELECT Count(*) FROM '+self.tabname).__next__()[0]
        info += '<Documents ct: ' + str(ct) + '>'
        
        return info
    
    def query(self, qstr, verbose=False):
        if self.verbose or verbose: print(qstr)
        return self.c.execute(qstr)
    
    #def getcols(self):
    #    return [t[1] for t in self.c.execute('PRAGMA table_info(' + self.tabname + ')')]
        
    # ifnotunique = 'REPLACE', 'IGNORE'
    def add(self, datadict, ifnotunique=None):
        cols = list(datadict.keys())
        payload = [datadict[c] if not (c in self.isblob.keys() and self.isblob[c]) else pickle.dumps(datadict[c]) for c in cols]
        n = len(cols)
        replacecode = ' OR ' + ifnotunique if ifnotunique is not None else ''
        
        self.c.execute('INSERT'+replacecode+' INTO ' + self.tabname + '('+','.join(cols)+') VALUES ('+','.join(['?']*n)+')', payload)
        
    def addmany(self, data, keys=None, ifnotunique=None):
        cols = list(keys) if keys is not None else data[0].keys()
        n = len(cols)
        
        if sum(self.isblob.values()) > 0:
            payload = ([d[c] if not self.isblob[c] else pickle.dumps(d[c]) for c in cols] for d in data)
            print('checking all')
        else:
            payload = data
        #payload = [datadict[c] if not (c in self.isblob.keys() and self.isblob[c]) else pickle.dumps(datadict[c]) for c in cols]
        replacecode = ' OR ' + ifnotunique if ifnotunique is not None else ''
        
        #print('INSERT'+replacecode+' INTO ' + self.tabname + '('+','.join(cols)+') VALUES ('+','.join(['?']*n)+')')
        
        self.c.executemany('INSERT'+replacecode+' INTO ' + self.tabname + '('+','.join(cols)+') VALUES ('+','.join(['?']*n)+')', payload)
    
    def delete(self, where):
        self.query('DELETE FROM '+ self.tabname + ' WHERE ' + where)
        
    
    def update(self, where, values):
        ''' Values is a dictionary. '''
        def makequery(values,where):
            q =  'UPDATE '+self.tabname+' SET ' + \
            ', '.join([k+' = ?' for k,v in values]) + \
            ' WHERE ' + where

            ''' UPDATE tasks
              SET priority = ? ,
                  begin_date = ? ,
                  end_date = ?
              WHERE id = ?'''

            return q

        if isinstance(values,dict):
            vals = list(values.items())
            query = makequery(vals,where)
            self.c.execute(query,[v for k,v in vals])
            
        elif isinstance(values,list):
            for val in values:
                vals = list(val.items())
                query = makequery(vals,where)
                self.c.execute(query,[v for k,v in vals])
        else:
            raise("Need to enter a list or dict to the update function.")

        return True
        
    def get(self, sel=None, where=None, orderby=None, limit=None, table=None, verbose=False, asdict=True):
        tabname = table if table is not None else self.tabname
        whereclause = ' WHERE '+where if where is not None else ''
        orderbyclause = (' ORDER BY '+orderby) if orderby is not None else ''
        limitclause = ' LIMIT ' + str(limit) if limit is not None else ''
        
        if sel is None:
            sel = self.columns
        
        n = len(sel)
        
        qstr = 'select '+','.join(sel)+' from '+tabname+whereclause+orderbyclause+limitclause
        if verbose: print(qstr)
        
        if asdict:
            for result in self.c.execute(qstr):
                
                    yield {
                        sel[i]:
                            result[i] if not (sel[i] in self.columns and self.isblob[sel[i]]) else pickle.loads(result[i]) 
                            for i in range(n)
                        }
        else:
            for result in self.c.execute(qstr):
                
                    yield [
                            result[i] if not (sel[i] in self.columns and self.isblob[sel[i]]) else pickle.loads(result[i]) 
                            for i in range(n)
                        ]
        
    def getdf(self, *args, **kwargs):
        results = list(self.get(*args, **kwargs))
        if len(results) > 0:
            sel = list(results[0].keys())
        else:
            try:
                sel
            except NameError:
                sel = list()
        return pd.DataFrame(results, columns=sel)




        
        
