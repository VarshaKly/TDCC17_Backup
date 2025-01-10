# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': "TDCC Student Plan",
    'version': "12.0.0.1.0",
    'depends': ['bista_tdcc_operations'],
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': "TDCC",
    'summary': "TDCC Student Plan",
    'description': """
        TDCC Student Plan
    """,
    'data': [
            'security/ir.model.access.csv',
            'views/student_plan_view.xml',
            'views/student_plan_template.xml',
            'report/student_plan_report_template.xml',
            'report/student_plan_report.xml',

        ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
