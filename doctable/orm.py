from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, MetaData, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker
from time import time
from sqlalchemy.sql import select

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
            self.name, self.fullname, self.nickname)

if __name__ == '__main__':
    engine = create_engine('sqlite:///:memory:', echo=True)
    Nusers = 500
    
    

    newusers = [User(name=str(i), fullname='a', nickname='d') for i in range(Nusers)]

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    start = time()
    session.add_all(newusers)
    r = session.query(User).all()
    print((time()-start), 'seconds')
    a = list(r)
