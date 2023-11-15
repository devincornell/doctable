import typing
import click
import inspect

from .connectcore import ConnectCore
from .dbtable import ReflectedDBTable
from .exposed import f, exp


def method_docs(obj: typing.Any):
    '''Return string listing methods and the docstrings of those methods.'''
    methods = [getattr(obj, mn) for mn in dir(obj) if not mn.startswith('_') and callable(getattr(obj, mn))]
    docs = list()
    for m in methods:
        if m.__doc__ is not None:
            docstr = '\t' + '\n\t'.join(m.__doc__.split('\n'))
        else:
            docstr = '\t[no docstring found]'
            
        docs.append(f'=========\n{m.__name__}\n{inspect.signature(m)}\n{docstr}\n')
    
    return '\n'.join(docs)


#CONTEXT_SETTINGS = dict()

@click.group()#context_settings=CONTEXT_SETTINGS)
def greet():
    pass

@greet.command(help='Execute a python expression "c" corresponds to the ConnectCore and "t" corresponds to a DBTable instance.')
@click.argument('target')
@click.option('-d', '--dialect', default='sqlite')
@click.option('--docs', is_flag=True, default=False)
@click.option('-t', '--table', default=None)
@click.argument('expression')
def execute(**kwargs) -> None:
    
    locals = {'f': f, 'exp': exp, 'docs': method_docs}
    
    locals['c'] = ConnectCore.open(
        target=kwargs['target'], 
        dialect=kwargs['dialect']
    )
    locals['c'].metadata_reflect()
    
    if kwargs['table'] is not None:
        locals['t'] = ReflectedDBTable.from_existing_table(
            table_name=kwargs['table'],
            core=locals['c'],
        )
    
    exp_string = f"{kwargs['expression']}"
    if kwargs['docs']:
        exp_string = f"docs({exp_string})"
    
    print(f'expression: {exp_string}')
    exec(f'print({exp_string})', {}, locals)    


if __name__ == '__main__':
    greet()
    