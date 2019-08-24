import pickle
import sqlalchemy.types as types

class TokensType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return '\t'.join(value) + '\n'
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.strip().split('\t')
        else:
            return None

    