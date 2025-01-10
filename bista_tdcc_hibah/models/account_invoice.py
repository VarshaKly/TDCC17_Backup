# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sponsor_id = fields.Many2one(comodel_name="res.partner", string="Sponsor",
                                 copy=False)
    percentage = fields.Float(string="Percentage", copy=False)
    sponsor_amount = fields.Float(string="Sponsor Amount", copy=False)
    is_hf = fields.Boolean(related="partner_id.is_hf")

    @api.model
    def line_get_convert(self, line, part):
        if line.get('name') == 'Sponsor Hibah Fund' and line.get('partner_id'):
            sponser_id = int(line.get('partner_id'))
            return self.env['product.product']. \
                _convert_prepared_anglosaxon_line(line, sponser_id)
        else:
            return self.env['product.product']. \
                _convert_prepared_anglosaxon_line(line, part)

    @api.multi
    def sponsor_details(self):
        """
            - Open Sponsor wizard form view
        """
        context = self._context.copy()
        context.update({'invoice_id': self.ids})
        return {
            'name': 'Sponsor Form',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sponsor.details',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    @api.multi
    def action_invoice_open(self):
        """ Check if Invoice amount and invoice payment lines amount total
        is same."""
        for rec in self:
            total = rec.amount_total
            if rec.is_hf:
                total = rec.amount_total - rec.sponsor_amount
            if rec.invoice_payment_line_ids and total != \
                    abs(sum(rec.invoice_payment_line_ids.mapped('amount'))):
                raise ValidationError(_('Invoice Total Amount and Invoice Payment '
                                'Lines total amount should be equal.'))
        return super(AccountInvoice, self).action_invoice_open()
    
    
    @api.multi
    def action_move_create(self):
        """
            - Creates invoice related analytics and financial move lines
            - Added code to create Sponsor journal item
        """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal\
                related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue

            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line +
            # eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly
            # adjust the other lines amount
            total, total_currency, iml = \
                inv.compute_invoice_totals(company_currency, iml)

            name = inv.name or ''
            if inv.payment_term_id:
                if inv.sponsor_amount:
                    total = total - inv.sponsor_amount
                #calculate journal entry based on invoice payment line
                #instead of payment term lines
                if inv.invoice_payment_line_ids and inv.type == 'out_invoice':
                    totlines = [(fields.Date.to_string(line.payment_date), line.amount) for line in inv.invoice_payment_line_ids]
                else:
                    totlines = inv.payment_term_id.\
                        with_context(currency_id=company_currency.id)\
                        .compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = \
                            company_currency\
                            ._convert(t[1], inv.currency_id, inv.company_id,
                                      inv._get_currency_rate_date() or
                                      fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],  # Added code to sub
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total - inv.sponsor_amount if
                    inv.sponsor_amount else total,  # Added code to sub
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            # To create sponsor journal item
            if inv.sponsor_amount:
                if not inv.sponsor_id.account_sponsor_id:
                    raise ValidationError(
                        _('Please add Sponsor Account on Sponsor form'))
                iml.append({
                    'type': 'dest',
                    'name': 'Sponsor Hibah Fund',
                    'partner_id': inv.sponsor_id.id,
                    'price': inv.sponsor_amount,
                    'account_id': inv.sponsor_id.account_sponsor_id.id,
                    'date_maturity': inv.date_invoice,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            # End of code
            part = self.env['res.partner']\
                ._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)
            line = inv.finalize_invoice_move_lines(line)
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            move = account_move.create(move_vals)
            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the
            # same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
            # Override this method and added code of account asset module
            context = dict(self.env.context)
            # Within the context of an invoice,
            # this default value is for the type of the invoice,
            # not the type of the asset.
            # This has to be cleaned from the context before creating
            # the asset,
            # otherwise it tries to create the asset
            # with the type of the invoice.
            context.pop('default_type', None)
            inv.invoice_line_ids.with_context(context).asset_create()
        return True
