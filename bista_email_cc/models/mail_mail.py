# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, vals):
        context = self._context
        if context.get('email_cc'):
            vals['email_cc'] = context.get('email_cc')
        return super(MailMail, self).create(vals)
