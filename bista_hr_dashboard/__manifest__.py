# -*- encoding: utf-8 -*-
#
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################

{
    'name': 'HR Dashboard',
    'version': '12.0.0.1.0',
    'category': 'HR',
    'description': """
    HR Dashboard
    """,
    'author': 'Bista Solutions Pvt. Ltd.',
    'website': 'http://www.bistasolutions.com',
    'depends': ['base', 'hr', 'event', 'bista_tdcc_announcement'],
    'data': [
            'views/dashboard_views.xml'
        ],
    'qweb': ["static/src/xml/hr_dashboard.xml"],
    'installable': True,
    'auto-install': False
}
