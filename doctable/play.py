from doctable2 import NewDocTable
import random

if __name__ == '__main__':
    example_schema = (
        ('id','integer',dict(primary_key=True)),
        ('title','string'),
        ('author','string'),
        ('model','bigblob'),
        ('model2','bigblob'),
        ('paragraphs','sentences'),
    )
    
    dt = NewDocTable(example_schema, fname=':memory:', verbose=False)
    
    mysents = [[str(i) for i in range(random.randrange(1,10))] for _ in range(3)]
    #mysents = example_schema
    mymodel = (1,2,3,float('-Inf'))
    mymodel2 = 'dude whats up'
    la = [
        {'title':'xxx', 'model':mymodel, 'model2':mymodel2}, 
        {'title':'yyy', 'model':mymodel, 'model2':mymodel2}, 
        {'title':'zzz', 'model':mymodel, 'model2':mymodel2},
    ]
    
    lb = [
        {'title':'xxx', 'paragraphs':mysents}, 
        {'title':'yyy', 'paragraphs':mysents}, 
        {'title':'zzz', 'paragraphs':mysents},
    ]
    
    lc = [
        {'title':'xxx', 'model':mymodel, 'paragraphs':mysents}, 
        {'title':'yyy', 'model':mymodel, 'paragraphs':mysents}, 
        {'title':'zzz', 'model':mymodel, 'paragraphs':mysents},
    ]
    
    #dt.insert(lc[0])
    
    #exit()
    dt.insert(la)
    
    #exit()
    #def xxx(dude):
    #    for d in dude:
    #        yield d
            
    #dt.insert(xxx(lc))
    
    #exit()
    
    for row in dt.select(dt['model2']):
        print(row)
    
    exit()
    #sents = ([str(i) for i in range(random.randrange(1,10))] for _ in range(10))
    #dt._insert_sents('sents', sents)
    
    
    
    #r = dt.execute(dt.select().where(dt['id'] > 5))
    #maxi = dt.selfirst(dt.max(dt['id']))
    #print(maxi)
    #sel = dt.selfirst(dt.max(dt._sent('doc_id')))
    #print(sel, 'shit################$$$$$$$$$$$$$$$$@@@@@@@@@@@@@@@@@@@@@@!!!!!!!!!!!!!!!!!!!!!!!!!!')
    #row = dt.selfirst()
    #print(row)
    
    #for sent in row['sents']:
    #    print(sent)
    #for row in dt.select():
        #print(id4, 'gmfd')
        #print('shitfuck')
    #    print(row)
    
    #for row in dt.select(where=dt['id']>5, limit=3):
        #print(dir(row))
        #print(row.has_key)
    #    print(row)
    
    
    #dt.insert({'title':'happy days', 'sents':sents})
    
    exit()
    
    #for r in dt.select():
    #    print(r)
    print('done')
    
    #rows = [{'title':'happy days {}'.format(i), 'sents':sents} for i in range(10)]
    #dt.insert(rows)
    #for r in dt.doc_table.select():
    #    print(r)

    
def ignoreme_for_now():
    engine = create_engine('sqlite:///:memory:', echo=False)
    Ndocs = 100
    Nsents = 3
    
    if True:
        metadata.create_all(engine)
        
        newdocs = list({'id':i,'title':str(i)+'_ha!','data':{'middle':'finger','c':'d'}} for i in range(Ndocs))
        newsents = [{'doc_id':i,'tokens':['a','b c','d'],'order':j} for j in range(Nsents) for i in range(Ndocs)]
        
        print(newdocs[0])
        
        with engine.connect() as conn:
            conn.execute(documents.insert(newdocs))
            conn.execute(sentences.insert(newsents))
        
        with engine.connect() as conn:
            bootstrap(conn, documents, sentences, 100)
            r = conn.execute(select([func.max(documents.c.id)])).where()
            #out_df = pd.read_sql(query.statement, engine)
            #temp_table.drop(engine)
            #print(next(r))
            #r = conn.execute(select([documents, sentences]).where(documents.c.id == sentences.c.doc_id))
            #for _ in range(10):
            #    print(next(r))
                
            #r = conn.execute(users.insert(), newusers)
            #r = conn.execute(select([users.c.id,]).where(users.c.__just_added==None))
            #for ri in r:
            #    print(ri, 'shit!')
        
            



    
    