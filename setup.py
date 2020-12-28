from setuptools import setup
from sphinx.setup_command import BuildDoc
cmdclass = {'build_sphinx': BuildDoc}

with open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

name='pyrefcount'
version='0.1'
release='0.1.0'

setup(
    name='pyrefcount',
    version=release,
    author='Paul Mundt',
    author_email='paul.mundt@adaptant.io',
    license='MIT',
    url='https://github.com/pmundt/pyrefcount',
    packages=['refcount'],
    long_description=long_description,
    long_description_content_type='text/x-rst',
    setup_requires=['pytest-runner', 'pytest-pylint'],
    tests_require=['pytest', 'pylint'],
    cmdclass=cmdclass,
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'source_dir': ('setup.py', 'docs'),
            'build_dir': ('setup.py', 'docs/_build'),
        },
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Object Brokering'
    ],
    keywords=['refcount'],
)
