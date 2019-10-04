import pickle
import sqlalchemy.types as types

class TokensType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return '\n'.join(value)
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.split('\n')
        else:
            return None

class ParagraphsType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return '\n\n'.join(['\n'.join(vs) for vs in value])
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return [v.split('\n') for v in value.split('\n\n')]
        else:
            return None
        
