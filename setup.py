
from setuptools import setup

setup(name='doctable',
    version='0.1',
    description='Python interface for single-table sqlite databases that allow for easy conversion to Pandas DataFrames.',
    url='https://github.com/devincornell/doctable',
    author='Devin J. Cornell',
    author_email='devinj.cornell@gmail.com',
    license='MIT',
    packages=['doctable'],
    requires=['sqlite3', 'pickle', 'pandas'],
    zip_safe=False,
     )


