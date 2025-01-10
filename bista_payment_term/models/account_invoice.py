# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#
from odoo import api, models, fields, _
from odoo.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    invoice_payment_line_ids = fields.One2many('invoice.payment.line',
                                               'invoice_id',
                                               string='Payment Lines')


    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        
        """ Inherit method to create journal entry from Invoice payment lines
            instead of payment term lines.  """
            
        if self.invoice_payment_line_ids and self.type == 'out_invoice':
            date_invoice = self.date_invoice
            if not date_invoice:
                date_invoice = fields.Date.context_today(self)
            if self.payment_term_id:
                pterm = self.payment_term_id
                pterm_list = [(fields.Date.to_string(line.payment_date),
                               line.amount)
                              for line in self.invoice_payment_line_ids]
                self.date_due = max(line[0] for line in pterm_list)
            elif self.date_due and (date_invoice > self.date_due):
                self.date_due = date_invoice
        else:
            return super(AccountInvoice, self.with_context(my_inv_id=self.id)
                         )._onchange_payment_term_date_invoice()
