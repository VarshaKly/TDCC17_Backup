# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#
{
    'name': "Bista TDCC Account",

    'summary': """
       Bista TDCC Account Changes""",

    'description': """
        Bista TDCC Account.
        This Module contains accounts related changes.
    """,

    'author': "Bista Solutions Pvt. Ltd",
    'website': "http://www.bistasolutions.com",

    'category': 'Account',
    'version': '12.0.0.1.0',

    'depends': ['bista_tdcc_operations', 'account_asset', 'account_reports'],

    'data': [
        'views/account_asset_view.xml',
        'views/journal_entry_view.xml',
    ],
}
