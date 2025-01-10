# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#
{
    'name': 'Payment Term',
    'version': '12.0.0.1.0',
    'summary': 'Payment Term Extension',
    'description': """
    Add Invoice amount breakup on Invoice level.
    """,
    'category': 'Invoicing Management',
    'website': 'http://www.bistasolutions.com',
    'data': ['security/ir.model.access.csv',
             'views/account_invoice_view.xml'],
    'depends': ['account'],
    'installable': True,
    'auto_install': False,
}
