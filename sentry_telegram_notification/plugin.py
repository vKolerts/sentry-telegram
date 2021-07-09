# coding: utf-8
import logging
from collections import defaultdict

from django import forms
from django.utils.translation import ugettext_lazy as _

from sentry.plugins.bases import notify
from sentry_plugins.base import CorePluginMixin
from sentry.utils.safe import safe_execute
from . import __version__, __doc__ as package_doc
import telegram
from telegram import ParseMode


class TelegramNotificationsOptionsForm(notify.NotificationConfigurationForm):
    api_origin = forms.CharField(
        label=_('Telegram API origin'),
        widget=forms.TextInput(attrs={'placeholder': 'https://api.telegram.org'}),
        initial='https://api.telegram.org'
    )
    api_token = forms.CharField(
        label=_('Bot API token'),
        widget=forms.TextInput(attrs={'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}),
        help_text=_('Read more: https://core.telegram.org/bots/api#authorizing-your-bot'),
    )
    receivers = forms.CharField(
        label=_('Receivers'),
        widget=forms.Textarea(attrs={'class': 'span6'}),
        help_text=_(
            'Enter receivers IDs (one per line). Personal messages, group chats and channels are also available' \
            'You can use username for groups and channels'))

    message_template = forms.CharField(
        label=_('Message template'),
        widget=forms.Textarea(attrs={'class': 'span4'}),
        help_text=_('Set in standard python\'s {}-format convention, available names are: '
                    '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}'),
        initial='*[Sentry]* {project_name} {tag[level]}: *{title}*\n```{message}```\n{url}'
    )


class TelegramNotificationsPlugin(CorePluginMixin, notify.NotificationPlugin):
    title = 'Telegram Notifications'
    slug = 'sentry_telegram_notification'
    description = package_doc
    version = __version__
    author = 'Faraz Fesharaki'
    author_url = 'https://github.com/FarazFe/sentry-telegram'
    resource_links = [
        ('Source', 'https://github.com/FarazFe/sentry-telegram'),
    ]

    conf_key = 'sentry_telegram_notification'
    conf_title = title

    project_conf_form = TelegramNotificationsOptionsForm

    def is_configured(self, project, **kwargs):
        return bool(self.get_option('api_token', project) and self.get_option('receivers', project))

    def get_config(self, project, **kwargs):
        return [
            {
                'name': 'api_origin',
                'label': 'Telegram API origin',
                'type': 'text',
                'placeholder': 'https://api.telegram.org',
                'validators': [],
                'required': True,
                'default': 'https://api.telegram.org'
            },
            {
                'name': 'api_token',
                'label': 'BotAPI token',
                'type': 'text',
                'help': 'Read more: https://core.telegram.org/bots/api#authorizing-your-bot',
                'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
                'validators': [],
                'required': True,
            },
            {
                'name': 'receivers',
                'label': 'Receivers',
                'type': 'textarea',
                'help': 'Enter receivers IDs (one per line). Personal messages, group chats and channels are also available' \
                        'You can use username for groups and channels',
                'validators': [],
                'required': True,
            },
            {
                'name': 'message_template',
                'label': 'Message Template',
                'type': 'textarea',
                'help': 'Set in standard python\'s {}-format convention, available names are: '
                        '{project_name}, {url}, {title}, {message}, {tag[%your_tag%]}. Undefined tags will be shown as [NA]',
                'validators': [],
                'required': True,
                'default': '*[Sentry]* {project_name} {tag[level]}: *{title}*\n```{message}```\n{url}'
            },
        ]

    def build_message(self, group, event):
        the_tags = defaultdict(lambda: '[NA]')
        the_tags.update({k: v for k, v in event.tags})
        names = {
            'title': event.title,
            'tag': the_tags,
            'message': event.message,
            'project_name': group.project.name,
            'url': group.get_absolute_url(),
        }

        template = self.get_message_template(group.project)

        text = template.format(**names)

        return {
            'text': text,
            'parse_mode': ParseMode.MARKDOWN,
        }

    def get_message_template(self, project):
        return self.get_option('message_template', project)

    def get_receivers(self, project):
        receivers = self.get_option('receivers', project)
        if not receivers:
            return []
        res = list(filter(bool, receivers.strip().splitlines()))
        return res

    def send_message(self, payload, receiver, bot):
        bot.send_message(chat_id=receiver, text=payload['text'], parse_mode=payload['parse_mode'])

    def notify_users(self, group, event, **kwargs):
        token = self.get_option('api_token', group.project)
        bot = telegram.Bot(token)
        receivers = self.get_receivers(group.project)
        payload = self.build_message(group, event)
        for receiver in receivers:
            safe_execute(self.send_message, payload, receiver, bot, _with_transaction=False)
