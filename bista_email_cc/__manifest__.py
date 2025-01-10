# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#

{
    'name': 'Compose Mail Email Address',
    'version': '1.1',
    'summary': 'Send mail direct on email address',
    'sequence': 1,
    'description': """
        Send mail direct on email address.
    """,
    'category': 'Mail',
    'author': "Bista Solutions",
    'website': "www.bistasolutions.com",
    'depends': ['mail'],
    'data': [
        'wizard/mail_compose_message_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': True,
}
