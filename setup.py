
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '0.8.8'
setup(name='doctable',
    version='{}'.format(version),
    description='Simple database interface for text analysis applications.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/devincornell/doctable',
    author='Devin J. Cornell',
    author_email='devinj.cornell@gmail.com',
    license='MIT',
    packages=['doctable'],
    install_requires=['sqlalchemy', 'pandas', 'numpy'],
    zip_safe=False,
    download_url='https://github.com/devincornell/doctable/archive/v{}.tar.gz'.format(version)
)


