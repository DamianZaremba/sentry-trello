#!/usr/bin/env python

"""
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
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Sentry-Trello. If not, see <http://www.gnu.org/licenses/>.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from requests.exceptions import RequestException
from sentry.plugins.bases.issue import IssuePlugin, NewIssueForm

from trello import TrelloApi
import sentry_trello


class TrelloSentry(TrelloApi):
    @staticmethod
    def reformat_to_markdown(data):
        # Lame attempt at re-formatting for markdown
        in_stack_trace = False
        ndata = ''
        stack_trace = ''
        for line in data.split("\n"):
            if not in_stack_trace and line.strip() == '```':
                in_stack_trace = True
            elif in_stack_trace and line.strip() == '```':
                break
            else:
                if in_stack_trace and line.strip() != _('Stacktrace (most recent call last):') and line.strip() != '':
                    if line[0:2] == ' ':
                        line = line[2:]
                    stack_trace += ' %s' % line
                else:
                    ndata += line
        ndata += '\n'
        ndata += stack_trace
        ndata += '\n'
        return ndata

    def organizations_to_options(self, member_id_or_username='me'):
        organizations = self.members.get_organization(member_id_or_username, fields='name')
        options = tuple()
        for org in organizations:
            options += ((org['id'], org['name']),)
        return options

    def boards_to_options(self, organization):
        boards = self.organizations.get_board(organization, fields='name')
        options = tuple()
        for board in boards:
            group = tuple()
            lists = self.boards.get_list(board['id'], fields='name')
            for l in lists:
                group += ((l['id'], l['name']),)
            options += ((board['name'], group),)
        return options


class TrelloSettingsForm(forms.Form):
    key = forms.CharField(label=_('Trello API Key'))
    token = forms.CharField(label=_('Trello API Token'))
    organization = forms.CharField(label=_('Organization to add a card to'), max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        super(TrelloSettingsForm, self).__init__(*args, **kwargs)
        initial = kwargs['initial']
        attrs = None
        organizations = ()
        help_text = None
        required = True
        try:
            trello = TrelloSentry(initial.get('key'), initial.get('token'))
            organizations = (('', ''),) + trello.organizations_to_options()
        except RequestException:
            attrs = {'disabled': 'disabled'}
            help_text = _('Set correct key and token and save before')
            required = False
        self.fields['organization'].widget = forms.Select(attrs=attrs, choices=organizations)
        self.fields['organization'].help_text = help_text
        self.fields['organization'].required = required


class TrelloForm(NewIssueForm):
    title = forms.CharField(label=_('Title'), max_length=200, widget=forms.TextInput(attrs={'class': 'span9'}))
    description = forms.CharField(label=_('Description'), widget=forms.Textarea(attrs={'class': 'span9'}))
    board_list = forms.CharField(label=_('Trello List'), max_length=50)

    def __init__(self, data=None, initial=None):
        super(TrelloForm, self).__init__(data=data, initial=initial)
        self.fields['board_list'].widget = forms.Select(choices=initial.get('trello_list', ()))


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

    new_issue_form = TrelloForm

    def can_enable_for_projects(self):
        return True

    def is_configured(self, request, project, **kwargs):
        return all((self.get_option(key, project) for key in ('key', 'token', 'organization')))

    def get_initial_form_data(self, request, group, event, **kwargs):
        initial = super(TrelloCard, self).get_initial_form_data(request, group, event, **kwargs)
        try:
            trello = TrelloSentry(self.get_option('key', group.project), self.get_option('token', group.project))
            boards = trello.boards_to_options(self.get_option('organization', group.project))
        except RequestException, e:
            raise forms.ValidationError(_('Error adding Trello card: %s') % str(e))
        initial.update({
            'board_list': self.get_option('board_list', group.project),
            'trello_list': boards
        })
        return initial

    def get_issue_label(self, group, issue_id, **kwargs):
        iid, iurl = issue_id.split('/', 1)
        return _('Trello-%s') % iid

    def get_issue_url(self, group, issue_id, **kwargs):
        iid, iurl = issue_id.split('/', 1)
        return iurl

    def get_new_issue_title(self, **kwargs):
        return _('Create Trello Card')

    def create_issue(self, request, group, form_data, **kwargs):
        description = TrelloSentry.reformat_to_markdown(form_data['description'])
        try:
            trello = TrelloApi(self.get_option('key', group.project), self.get_option('token', group.project))
            card = trello.cards.new(name=form_data['title'], desc=description, idList=form_data['board_list'])
            return '%s/%s' % (card['id'], card['url'])
        except RequestException, e:
            raise forms.ValidationError(_('Error adding Trello card: %s') % str(e))