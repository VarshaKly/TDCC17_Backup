# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#

from odoo import models, api, _
from odoo.exceptions import Warning


class StatementAccount(models.AbstractModel):
    _name = 'report.bista_tdcc_hibah.report_account_statement_tdcc'
    _description = 'Statement of account Payment'

    def _get_data_from_report(self, data):
        partner_id = self.env['res.partner'].browse(
            int(data.get('partner_id')))
        if data.get('date', False):
            dt1 = data.get('date')
            where = "where ai.type in ('out_invoice', 'out_refund') and \
                     ai.residual != 0.00 and ai.state = 'open' \
                     and ai.date_invoice <='" + dt1 + "' and ai.partner_id = " \
                    + str(partner_id.id)
        query = """
                    select
                    ai.number as number,
                    ai.type as invoice_type,
                    to_char(ai.date_invoice, 'DD/MM/YYYY') as date,
                    rp.name as client_name,
                    string_agg(ail.name, ',\n') as desc,
                    rp1.name as attendant,
                    ai.amount_total as total,
                    (ai.amount_total-ai.residual) as receipts,
                    ai.residual as balance
                from
                    account_invoice ai
                    left join account_invoice_line ail on ail.invoice_id=ai.id
                    left join res_partner rp on ai.partner_id = rp.id
                    left join res_partner rp1 on
                    ai.attendant_id=rp1.id """ + where + """
                group by
                    ai.id,
                    rp.name,
                    rp1.name
                order by
                    ai.date_invoice
                """
        self._cr.execute(query)
        res = self._cr.dictfetchall()
        if not res:
            raise Warning(_('There is not data to print for this Client.'))
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        statement_report = self.env['ir.actions.report']._get_report_from_name(
            'bista_tdcc_hibah.report_account_statement_tdcc')
        partner_id = self.env['res.partner'].browse(
            data.get('form_data').get('partner_id'))
        return {
            'doc_ids': partner_id.ids,
            'docs': partner_id,
            'doc_model': statement_report.model,
            'date': data.get('form_data').get('date'),
            'partner': data['form_data']['partner_id'],
            'get_data_from_report': self._get_data_from_report(
                data.get('form_data')),
        }
