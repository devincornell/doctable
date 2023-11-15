import argparse
import click
import io

from .connectcore import ConnectCore
from .dbtable import ReflectedDBTable
from .exposed import f, exp


@click.group()
def greet():
    pass

@greet.command()
@click.argument('target')
@click.option('-d', '--dialect', default='sqlite')
@click.option('-t', '--table', default=None)
@click.argument('expression')
def execute(**kwargs) -> None:
    locals = {'f': f, 'exp': exp}
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
    print(f'expression: {exp_string}')
    exec(f'print({exp_string})', {}, locals)    


if __name__ == '__main__':
    greet()
    