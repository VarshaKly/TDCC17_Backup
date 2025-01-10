# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models


class MailMail(models.TransientModel):
    _inherit = 'mail.compose.message'

    email_cc = fields.Char('Cc', help="Carbon copy recipients")

    @api.multi
    def action_send_mail(self):
        return self.with_context(email_cc=self.email_cc).send_mail()
