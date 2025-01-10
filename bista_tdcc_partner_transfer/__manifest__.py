# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': "Transfer amount between siblings",
    'version': "12.0.0.1.0",
    'depends': [
        'bista_tdcc_operations',
    ],
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': "TDCC",
    'summary': """
        Transfer Amount Between Siblings
    """,
    'description': """
    """,
    'data': [
        'data/credit_transfer_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/sibling_credit_transfer_view.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
