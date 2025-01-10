# -*- encoding: utf-8 -*-
#
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################

{
    'name': 'SMS Global',
    'category': 'Base',
    'version': '12.0.1.0',
    'author': 'Bista Solutions Pvt. Ltd.',
    'website': 'http://www.bistasolutions.com',
    'description': """SMS Global""",
    'summary': 'Send SMS with SMS Global Gateway',
    'depends': ['base'],
    'data': [
            'security/ir.model.access.csv',
            'data/sms_global_cron.xml',
            'wizard/message_compose_view.xml',
            'views/ir_sms_server_views.xml',
            'views/sms_template_views.xml',
            'views/message_message_views.xml',
        ],
    'images': [],
    'installable': True,
    'auto_install': False,
}
