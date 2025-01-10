# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#
{
    'name': "Bista Product Pack",

    'summary': """
       Bista Product Pack""",

    'description': """
       Bista Product Pack
    """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",

    'category': 'Sales',
    'version': '12.0.0.1.0',

    'depends': ['sale_management'],

    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/sale_view.xml',
        'views/product_wizard_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
