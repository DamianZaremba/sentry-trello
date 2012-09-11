#!/usr/bin/env python
'''
Sentry-Trello
=============

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
from django import forms

from sentry.conf import settings
from sentry.plugins import Plugin

from trello import TrelloApi
import sentry_trello

class TrelloSettingsForm(forms.Form):
    key = forms.CharField(help_text='Trello API Key')
    token = forms.CharField(help_text='Trello API Token')
    board_list = forms.CharField(help_text='ID of the list to add a card to')

class TrelloCard(Plugin):
    author = 'Damian Zaremba'
    author_url = 'http://damianzaremba.co.uk'
    title = 'Trello'
    resource_links = [
        ('Bug Tracker', 'https://github.com/damianzaremba/sentry-trello/issues'),
        ('Source', 'https://github.com/damianzaremba/sentry-trello'),
    ]

    conf_title = 'Trello'
    conf_key = 'trello'

    version = sentry_trello.VERSION
    project_conf_form = TrelloSettingsForm

    def can_enable_for_projects(self):
        return True

    def is_setup(self, project):
        return (
            all((self.get_option(key, project)
                for key in ('key', 'token', 'board_list'))
            )
        )

    def post_process(self, group, event, is_new, is_sample, **kwargs):
        if not is_new or not self.is_setup(event.project):
            return

        title = '%s: %s' % (event.get_level_display().upper(),
                            event.error().split('\n')[0])

        link = '%s/%s/group/%d/' % (settings.URL_PREFIX, group.project.slug,
                                    group.id)

        message = 'Server: %s\n' % event.server_name
        message += 'Group: %s\n' % event.group
        message += 'Logger: %s\n' % event.logger
        message += 'Message: %s\n' % event.message
        message += '\n%s\n' % link

        self.make_card(title, message, event)

    def make_card(self, title, message, event):

        trello = TrelloApi(self.get_option('key', event.project),
                            self.get_option('token', event.project))
        trello.cards.new(name=title, desc=message,
                        idList=self.get_option('board_list', event.project))
