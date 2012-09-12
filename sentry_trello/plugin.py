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
from django.utils.translation import ugettext_lazy as _

from sentry.conf import settings
from sentry.plugins.bases.issue import IssuePlugin

from trello import TrelloApi
import sentry_trello

class TrelloSettingsForm(forms.Form):
    key = forms.CharField(help_text=_('Trello API Key'))
    token = forms.CharField(help_text=_('Trello API Token'))
    board_list = forms.CharField(help_text=_('ID of the list to add a card to'))

class TrelloCard(IssuePlugin):
    author = 'Damian Zaremba'
    author_url = 'http://damianzaremba.co.uk'
    title = _('Trello')
    description = _('Create Trello cards on exceptions.')
    slug = 'trello'

    resource_links = [
        (_('How do I configure this?'),
            'https://github.com/damianzaremba/sentry-trello/blob/master/HOW_TO_SETUP.md'),
        (_('Bug Tracker'), 'https://github.com/damianzaremba/sentry-trello/issues'),
        (_('Source'), 'https://github.com/damianzaremba/sentry-trello'),
    ]

    conf_title = title
    conf_key = 'trello'

    version = sentry_trello.VERSION
    project_conf_form = TrelloSettingsForm

    def can_enable_for_projects(self):
        return True

    def is_configured(self, project):
        return (
            all((self.get_option(key, project)
                for key in ('key', 'token', 'board_list'))
            )
        )

    def create_issue(self, request, group, form_data, **kwargs):
        title = '%s: %s' % (group.get_level_display().upper(),
                            group.error().split('\n')[0])

        link = '%s/%s/group/%d/' % (settings.URL_PREFIX, group.project.slug,
                                    group.id)

        message = 'Server: %s\n' % group.server_name
        message += 'Group: %s\n' % group.group
        message += 'Logger: %s\n' % group.logger
        message += 'Message: %s\n' % group.message
        message += '\n%s\n' % link

        try:
            self.make_card(title, message, group)
        except Exception, e:
            raise forms.ValidationError(
                _('Error adding Trello card: %s') %
                str(e))

    def make_card(self, title, message, group):

        trello = TrelloApi(self.get_option('key', group.project),
                            self.get_option('token', group.project))
        trello.cards.new(name=title, desc=message,
                        idList=self.get_option('board_list', group.project))
