import gc
import pytest
import sqlalchemy
#from doctable.schemas import parse_schema
import time
import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable
#from doctable.schemas import parse_schema
import pickle


engine = doctable.ConnectEngine(target=':memory:')

class User(engine.Base):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(50))
    addresses = sqlalchemy.relationship("Address", backref="user")

class Address(engine.Base):
    __tablename__ = 'addresses'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String(50))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))

engine.create_all()

if __name__ == '__main__':
    ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
