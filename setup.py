#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

from sentry_telegram_notification import __version__

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='sentry_telegram_notification',
    version=__version__,
    packages=['sentry_telegram_notification'],
    install_requires=[
        'python-telegram-bot==13.7',
    ],
    url='https://github.com/FarazFe/sentry-telegram',
    author='Faraz Fesharaki',
    author_email='fesharakifaraz@gmail.com',
    description='Plugin for Sentry which allows sending notification via Telegram messenger.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='MIT',
    entry_points={
        'sentry.plugins': [
            'sentry_telegram_notification = sentry_telegram_notification.plugin:TelegramNotificationsPlugin',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: System :: Monitoring',
    ],
    include_package_data=True,
)
