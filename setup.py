#! /usr/bin/env python
from setuptools import setup
from os import path

import pypandoc

here = path.abspath(path.dirname(__file__))

readme_fname = path.join(here, 'README.md')
long_description = pypandoc.convert(readme_fname, 'rst')

setup(
    # Project metadata
    name='lifts',
    version=open(path.join(here, 'VERSION')).read().strip(),
    license='GPLv3+',
    description='An AI game, simulating a building with lifts',
    long_description=long_description,
    url='https://github.com/quasipedia/lifts',

    # Author details
    author='Mac Ryan',
    author_email='quasipedia@gmail.com',

    # Classifiers & Keywords
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Games/Entertainment',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='AI game lifts simulation artificial-intelligence',

    # Package contents
    packages=['lifts'],

    # Dependencies
    install_requires=['simpleactors', 'Logbook', 'toml', 'docopt'],
    extras_require={
        'dev': ['pypandoc', 'wheel>=0.24.0', 'twine'],
        'test': ['nose', 'rednose', 'coverage'],
    },

    entry_points={
        'console_scripts': [
            'lifts=lifts.simulation:main',
        ],
    },

)
