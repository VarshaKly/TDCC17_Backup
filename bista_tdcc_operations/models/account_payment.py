# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime, date


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        if self._context.get('active_model', False) == 'account.invoice':
            active_id = self._context.get('active_id')
            invoice = self.env['account.invoice'].browse(active_id)
            rec.update({
                'user_id': invoice.user_id.id or False,
                'physician_id': invoice.user_id.partner_id.id or False,
            })
        return rec

    @api.depends()
    def _get_available_balance(self):
        for payment in self:
            if payment.payment_type == 'inbound':
                cml_id = payment.move_line_ids.filtered(
                    lambda ml: ml.account_id.internal_type == 'receivable')
                payment.available_balance = abs(
                    cml_id.amount_residual) if cml_id else 0.00

    service_type_id = fields.Many2one('service.type', string="Service Type",
                                      copy=False)
    physician_id = fields.Many2one('res.partner',
                                   string='Physician',
                                   domain=[('is_physician', '=', True)])
    physician_type = fields.Selection([('single', 'Single'),
                                       ('multi', 'Multi')],
                                      string='Physician Type',
                                      default='single')
    multi_physician_ids = fields.One2many('account.payment.physician',
                                          'payment_id',
                                          string='Practitioners ')
    payment_info = fields.Char(string='Payment Information')
    tdcc_voucher_id = fields.Integer(string="TDCC Voucher Ref.")
    tdcc_voucher_sequence = fields.Char(string="TDCC Voucher No.")
    tdcc_cheque_date = fields.Date(string='TDCC Cheque Date')
    tdcc_cheque_due_date = fields.Date(string='TDCC Cheque Due Date')
    tdcc_cheque_no = fields.Char(string='TDCC Cheque Number')
    allow_cancel = fields.Boolean(string="Allow Cancel")
    payment_cancel_req_user_id = fields.Many2one('res.users',
                                                 string="Cancel Request By")
    payment_cancel_req_date = fields.Datetime(string="Cancel Request Date")
    payment_cancel_req_sent = fields.Boolean(string="Cancel Request sent")
    cancel_reason = fields.Text(string="Cancel Reason")
    approval_by = fields.Many2one('res.users', string="Approved By")
    approval_date = fields.Datetime(string="Approval Date")
    cancelled_by = fields.Many2one('res.users', string="Cancelled By")
    cancelled_date = fields.Datetime(string="Cancel Date")
    available_balance = fields.Float(string="Available Balance",
                                     compute=_get_available_balance)

    @api.multi
    def cancel(self):
        """ Check if payment cancellation approved by co-founder or it is
        from PDC bounce cheque"""
        if not self.allow_cancel and not self._context.get('cheque_bounce') and \
            self.partner_type == 'customer' and self.payment_type == 'inbound':
            raise Warning(_('You can not cancel payment \
                                untill approved by Co-founders'))
        self.write({'cancelled_by': self.env.user.id,
                    'cancelled_date': datetime.now()})
        return super(AccountPayment, self).cancel()

    @api.multi
    def action_draft(self):
        self.write({'payment_cancel_req_date': False,
                    'payment_cancel_req_sent': False,
                    'allow_cancel': False})
        return super(AccountPayment, self).action_draft()

    @api.multi
    def action_approve_cancel_payment(self):
        cofounder_group_id = 'bista_tdcc_operations.group_tdcc_cofounder'
        if self.env.user.has_group(cofounder_group_id):
            if not self.payment_cancel_req_sent:
                raise Warning(_('You can not perform this action without \
                                request for cancellation'))
            self.write({'allow_cancel': True,
                        'approval_by': self.env.user.id,
                        'approval_date': datetime.now()})
        else:
            raise Warning(_('You are not allowed to approve \
                            cancel payment request'))

    @api.multi
    def action_send_payment_mail(self):
        self.ensure_one()
        try:
            template_id = self.env.ref(
                'bista_tdcc_operations.account_payment_mail_template_with_attachment')
        except ValueError:
            template_id = False
        try:
            compose_form_id = self.env.ref(
                'mail.email_compose_message_wizard_form')
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'account.payment',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id and template_id.id,
            'default_composition_mode': 'comment',
            # 'custom_layout': "mail.mail_notification_borders",
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id.id, 'form')],
            'view_id': compose_form_id.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        for rec in self:
            # Get payment info from invoice
            if rec.invoice_ids:
                invoice_id = rec.invoice_ids[0]
                rec.payment_info = invoice_id.payment_info
#             invoice_line_ids = self.env['account.invoice.line'].search(
#                 [('invoice_id', 'in', rec.invoice_ids.ids)])
#             for line in invoice_line_ids:
#                 rec.service_type_id = line.service_type_id.id
            rec.service_type_id = rec.service_type_id.id or False
            # Send auto email to customer on payment confirm
            if rec.payment_type == 'inbound' and rec.partner_type == 'customer' \
                and rec.payment_method_code != 'pdc':
                template_id = rec.env.ref(
                    'bista_tdcc_operations.account_payment_mail_template_without_attachment')
                template_id.send_mail(rec.id, force_send=True)
        return res

    @api.multi
    @api.constrains('amount', 'multi_physician_ids', 'physician_type')
    def check_multi_physician_amount(self):
        for rec in self:
            if rec.physician_type == 'multi' and rec.multi_physician_ids:
                total_amt = 0.0
                for phy in rec.multi_physician_ids:
                    total_amt += phy.amount
                if rec.amount != total_amt:
                    raise Warning(_('Practitioners total amount and Payment total \
                                        amount must be same.'))

    @api.onchange('physician_type')
    def onchange_physician_type(self):
        if self.physician_type and self.physician_type == 'single':
            self.multi_physician_ids = False
        elif self.physician_type and self.physician_type == 'multi':
            self.physician_id = False

    @api.multi
    def view_open_invoices(self):
        return {
            'name': _('Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.partner_id.id),
                       ('state', '=', 'open'), ('type', '=', 'out_invoice')],
        }

    @api.multi
    def get_advance_payment_amount(self):
        amount = 0.00
        for payment in self:
            cml_id = payment.move_line_ids.filtered(
                lambda ml: ml.account_id.internal_type == 'receivable')
            amount = abs(cml_id.amount_residual)
        return amount

    @api.multi
    def get_vendor_payment_amount(self):
        amount = 0.00
        for payment in self:
            debit_line_id = payment.move_line_ids.filtered(
                lambda ml: ml.account_id.internal_type == 'payable')
            amount = abs(debit_line_id.debit - debit_line_id.amount_residual)
            if self._context.get('invoice_id'):
                invoice_id = self.env['account.invoice'].browse(
                    self._context.get('invoice_id'))
                payment_log_id = invoice_id.payment_log_ids.filtered(
                    lambda line: line.payment_id and line.payment_id.id != self.id and line.date <= date.today())
                paid_amount = sum(
                    line.amount for line in payment_log_id) or 0.00
                return paid_amount
        return amount

    def action_validate_invoice_payment(self):
        res = super(AccountPayment, self).action_validate_invoice_payment()
        invoice_id = self.env['account.invoice'].browse(
            self._context.get('active_id'))
        vals = {'invoice_id': invoice_id.id, 'payment_id': self.id,
                'amount': self.amount, 'date': self.payment_date}
        if invoice_id.type == 'in_invoice':
            debit_aml = invoice_id.payment_move_line_ids.filtered(
                lambda aml: aml.account_id.id == invoice_id.account_id.id
                        and aml.debit != 0.00)
            vals.update({'move_line_id': debit_aml and debit_aml[0].id})
        if invoice_id.type == 'out_invoice':
            credit_aml = invoice_id.payment_move_line_ids.filtered(
                lambda aml: aml.account_id.id == invoice_id.account_id.id
                        and aml.credit != 0.00)
            vals.update({'move_line_id': credit_aml and credit_aml[0].id})
        invoice_id.write({'payment_log_ids': [(0, 0, vals)]})
        return res


class AccountPaymentPhysician(models.Model):
    _name = 'account.payment.physician'
    _description = 'Account Payment Physician'

    physician_id = fields.Many2one('res.partner', 'Practitioner')
    amount = fields.Float(strig='amount')
    payment_id = fields.Many2one('account.payment',
                                 'Account Payment')


class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"

    physician_id = fields.Many2one('res.partner',
                                   string='Physician',
                                   domain=[('is_physician', '=', True)])
    physician_type = fields.Selection([('single', 'Single'),
                                       ('multi', 'Multi')],
                                      string='Physician Type',
                                      default='single')

    multi_physician_ids = fields.One2many('account.payment.physician',
                                          'payment_id',
                                          string='Practitioners ')
    user_id = fields.Many2one('res.users', string='Salesperson')
    service_type_id = fields.Many2one('service.type', string='Service Type')

    @api.multi
    def _prepare_payment_vals(self, invoices):
        res = super(account_register_payments, self)._prepare_payment_vals(
            invoices)
        res.update({
            'physician_type': self.physician_type,
            'physician_id': self.physician_id.id or False,
            'multi_physician_ids':
                [(6, 0, self.multi_physician_ids.ids)] or False,
            'service_type_id': self.service_type_id.id or False
        })
        return res

    @api.onchange('physician_type')
    def onchange_physician_type(self):
        if self.physician_type and self.physician_type == 'single':
            self.multi_physician_ids = False
        elif self.physician_type and self.physician_type == 'multi':
            self.physician_id = False

    @api.multi
    def create_payments(self):
        res = super(account_register_payments, self).create_payments()
        inv_pay_log = self.env['invoice.payment.log']
        for invoice in self.invoice_ids:
            if invoice.type == 'in_invoice':
                aml_id = invoice.payment_move_line_ids.filtered(
                    lambda aml: aml.account_id.id == invoice.account_id.id
                    and aml.debit != 0.00)
                partial_reconcile_credit_id = aml_id and aml_id[0].matched_credit_ids.filtered(
                    lambda cml: cml.credit_move_id.invoice_id.id == invoice.id)
                if partial_reconcile_credit_id:
                    amount = partial_reconcile_credit_id.amount
                else:
                    amount = aml_id and aml_id[0].debit or 0.00
            if invoice.type == 'out_invoice':
                aml_id = invoice.payment_move_line_ids.filtered(
                    lambda aml: aml.account_id.id == invoice.account_id.id
                    and aml.credit != 0.00)
                reconcile_cr_id = aml_id and aml_id[0].matched_debit_ids.filtered(
                    lambda dml: dml.debit_move_id.invoice_id.id == invoice.id)
                if reconcile_cr_id:
                    amount = sum(reconcile_cr_id.mapped('amount')) or 0.00
                else:
                    amount = aml_id and aml_id[0].credit or 0.00
            inv_pay_log_id = inv_pay_log.search([
                ('payment_id', '=', aml_id and aml_id[0].payment_id.id),
                ('move_line_id', '=', aml_id and aml_id[0].id),
                ('invoice_id', '=', invoice.id)])
            if not inv_pay_log_id:
                invoice.write({'payment_log_ids': [
                    (0, 0, {'payment_id': aml_id and
                            aml_id[0].payment_id.id or False,
                            'amount': amount,
                            'move_line_id': aml_id and aml_id[0].id,
                            'date': date.today()})]})
        return res
