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
import requests

from django import forms
from django.utils.translation import ugettext_lazy as _

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

    def is_configured(self, request, project):
        return (
            all((self.get_option(key, project)
                for key in ('key', 'token', 'board_list'))
            )
        )

    def get_issue_label(self, group, issue_id, **kwargs):
        iid, iurl = issue_id.split('/', 1)
        return 'Trello-%s' % iid

    def get_issue_url(self, group, issue_id, **kwargs):
        iid, iurl = issue_id.split('/', 1)
        return iurl

    def get_new_issue_title(self, **kwargs):
        return 'Create Trello Card'

    def create_issue(self, request, group, form_data, **kwargs):
        title = form_data['title']
        description = ''
        
        # Lame attempt at re-formatting for markdown
        in_stack_trace = False
        stack_trace = ''
        for line in form_data['description'].split("\n"):
            if not in_stack_trace and line.strip() == '```':
                in_stack_trace = True

            elif in_stack_trace and line.strip() == '```':
                break
            else:
                if in_stack_trace and \
                line.strip() != 'Stacktrace (most recent call last):' \
                and line.strip() != '':
                    if line[0:2] == '  ':
                        line = line[2:]
                    stack_trace += '    %s' % line
                else:
                    description += line

        description += '\n'
        description += stack_trace
        description += '\n'

        try:
            return self.make_card(title, description, group)
        except requests.exceptions.RequestException, e:
            raise forms.ValidationError(
                _('Error adding Trello card: %s') %
                str(e))

    def make_card(self, title, message, group):

        trello = TrelloApi(self.get_option('key', group.project),
                            self.get_option('token', group.project))
        card = trello.cards.new(name=title, desc=message,
                        idList=self.get_option('board_list', group.project))
        return '%s/%s' % (card['id'], card['url'])
