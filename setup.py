#!/usr/bin/env python
'''
Sentry-Trello
=============
A Sentry plugin to add cards to a Trello board.

License
-------
Copyright 2012 Damian Zaremba

This file is part of Sentry-Trello.

Sentry-Trello is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Sentry-Trello is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Sentry-Trello.  If not, see <http://www.gnu.org/licenses/>.
'''
from setuptools import setup, find_packages

setup(
    name='sentry-trello',
    version='1.0.7',
    author='Damian Zaremba',
    author_email='damian@damianzaremba.co.uk',
    url='https://github.com/DamianZaremba/sentry-trello',
    description='A Sentry plugin that integrates with Trello',
    long_description=__doc__,
    license='GPL',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'trello',
    ],
    entry_points={
        'sentry.plugins': [
            'trello = sentry_trello.plugin:TrelloCard'
        ]
    },
    include_package_data=True,
)
