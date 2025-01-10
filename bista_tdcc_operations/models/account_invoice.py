# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import date
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    service_type_id = fields.Many2one('service.type',
                                      string="Service Type")
    service_group_id = fields.Many2one('service.group', string="Service Group")
    appointment_type_id = fields.Many2one('appointment.type',
                                          string="Appointment Type")
    tdcc_invoice_line_id = fields.Integer(string="TDCC Invoice Line Ref.")


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_default_service_type(self):
        if self.type == 'out_invoice':
            return True
        return False

    appointment_id = fields.Many2one(comodel_name='appointment.appointment',
                                     string="Appointment", copy=False)
    program_type = fields.Selection(related='team_id.program_type',
                                    string="Program Type")
    class_id = fields.Many2one('school.classroom', string="Class")
    payment_info = fields.Char(string='Payment Information')
    with_service_type = fields.Boolean(string="Report With Service Type",
                                       default=_get_default_service_type)
    tdcc_invoice_id = fields.Integer(string="TDCC Invoice Ref.")
    group_appointment_booking_id = fields.Many2one('group.appointment.booking',
                                                   string='Group Appointment'
                                                   'Booking', copy=False)
    with_description = fields.Boolean(string='Report with Description')
    vat_description = fields.Text(string='VAT description')
    cancel_date = fields.Date(string="Cancel Date")
    cancel_reason = fields.Text(string="Cancel Reason")
    invoice_cancel_req = fields.Boolean(string='Invoice Cancel Request From'
                                        'Appointment')
    invoice_cancel_req_user_id = fields.Many2one('res.users',
                                                 string='Invoice cancel'
                                                 'requested user')
    inv_cancel_req_date = fields.Datetime(string='Invoice Cancel Request Date')
    attendant_id = fields.Many2one('res.partner',
                                   string="Attendant",
                                   domain=[('is_student', '=', True)])
    payment_log_ids = fields.One2many('invoice.payment.log', 'invoice_id',
                                      string="Invoice Payments", copy=False)
    invoice_cancel_reason_id = fields.Many2one('appointment.cancel.reason',
                                               copy=False,
                                               string="Invoice Cancel Reason",
                                               track_visibility='onchange', )

    @api.multi
    def assign_outstanding_credit(self, credit_aml_id):
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        payment_amount = abs(credit_aml.amount_residual or
                             credit_aml.amount_residual_currency)
        if payment_amount > self.residual:
            payment_amount = self.residual
        res = super(AccountInvoice, self).assign_outstanding_credit(
            credit_aml_id)
        self.write({'payment_log_ids': [
            (0, 0, {'invoice_id': self.id,
                    'payment_id': credit_aml.payment_id and
                    credit_aml.payment_id.id or False,
                    'amount': payment_amount,
                    'move_line_id': credit_aml.id,
                    'date': date.today()}
             )]})
        return res

    @api.constrains('date_invoice')
    def _check_past_invoice_date(self):
        if self.type in ('out_refund', 'in_refund'):
            if self.date_invoice and self.date_invoice < date.today():
                raise ValidationError(
                    _('Credit Note Date can not be past date.'))

    @api.multi
    def action_invoice_cancel(self):
        res = super(AccountInvoice, self).action_invoice_cancel()
        for inv in self:
            if inv.program_type == '360' and not inv.invoice_cancel_req and \
                inv.type == 'out_invoice':
                raise Warning(_(
                    'You can not cancel this invoice without \
                            request from CRE !'))
            if not (inv.invoice_cancel_reason_id or inv.cancel_reason):
                raise Warning(_(
                    'You cannot process without cancellation reason !'))
            inv.update({'cancel_date': date.today(),
                        'invoice_cancel_req' : False})
        return res

#     @api.multi
#     def _message_auto_subscribe_notify(self, partner_ids, template):
# Prevent send mail to followers_ids
#         partner_ids = []
#         res = super(AccountInvoice, self)._message_auto_subscribe_notify(partner_ids, template)
#         return res

    @api.model
    def create(self, vals):
        if not vals.get('date_invoice'):
            vals.update({'date_invoice': fields.Date.today()})
        return super(AccountInvoice, self).create(vals)
#         return super(AccountInvoice, self.with_context(mail_create_nosubscribe=True,
#                                                        mail_create_nolog=True)).create(vals)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def remove_move_reconcile(self):
        res = super(AccountMoveLine, self).remove_move_reconcile()
        inv_pay_log = self.env['invoice.payment.log']
        for move_line in self:
            domain = [('move_line_id', '=', move_line.id)]
            if move_line.payment_id:
                domain += [('payment_id', '=', move_line.payment_id.id)]
            if move_line.invoice_id:
                domain += [('invoice_id', '=', move_line.invoice_id.id)]
            elif self._context.get('invoice_id', False):
                domain += [
                    ('invoice_id', '=', self._context.get('invoice_id'))]
            payment_log_ids = inv_pay_log.search(domain)
            if payment_log_ids:
                payment_log_ids.sudo().unlink()
        return res
