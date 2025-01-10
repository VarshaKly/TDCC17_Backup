# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': "l10n_tdcc_coa",

    'summary': """
        TDCC Chart Of Account""",

    'description': """
        TDCC Chart Of Account
    """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': 'Localization',
    'version': '12.0.0.1.0',
    'depends': ['account_accountant'],

    'data': [
        'data/tdcc_chart_of_account_data.xml',
        'data/tdcc_taxes_data.xml',
    ],
}
