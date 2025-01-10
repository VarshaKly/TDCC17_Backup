# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#
from odoo import models, api, _
from odoo.exceptions import Warning


class AccountReportSaleServiceTypeSummary(models.AbstractModel):
    _name = 'report.bista_account_reports.sales_by_service_type_summary'
    _description = 'TDCC Account Reports for Sales by Service Type Summary'

    def _get_data_from_report(self, data):

        dt1 = data['start_date']
        dt2 = data['end_date']
        where = "where ai.state not in ('cancel','draft') and \
            ail.service_type_id is not NULL and \
                    ai.date_invoice >='" + \
            dt1 + "' and ai.date_invoice <='" + dt2 + "'"
        if data.get('service_type_id'):
            where += " and ail.service_type_id = " + \
                str(data['service_type_id'])
        query = """select
                    x.treatment_name as service_name,
                    x.invoice_type as invoice_type,
                    sum(x.sales) as sales
                    --sum(x.receipts) as receipts,
                    --sum(x.balance) as balance
                from
                    (select
                        ai.date_invoice as date,
                        rp.name as partner_name,
                        ai.type as invoice_type,
                        tt.name as treatment_name,
                        ail.price_subtotal as sales
                        --ai.amount_total-ai.residual as receipts,
                        --ai.residual as balance
                    from
                        account_invoice ai
                        left join account_invoice_line ail
                        on ai.id=ail.invoice_id
                        left join res_partner rp on rp.id=ai.partner_id
                        left join service_type tt
                        on tt.id=ail.service_type_id """ + """
                    """ + where + """
                    ) x
                group by
                    x.treatment_name,
                    x.invoice_type
                order by
                    x.treatment_name,
                    x.invoice_type """

        self._cr.execute(query)
        res = self._cr.dictfetchall()
        if not res:
            raise Warning(_("There is no data with selected options."))
        return res

    def _get_title(self, data):
        return "Sales by  Service Type from %s to %s" % (
            data.get('start_date'),
            data.get('end_date'))

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_report = self.env['ir.actions.report']._get_report_from_name(
            'bista_account_reports.sales_by_service_type_summary')
        return {
            'doc_ids': self.ids,
            'docs': self,
            'get_title': self._get_title(data['form_data']),
            'doc_model': payment_report.model,
            'clients': data['form_data']['client_id'],
            'service_type': data['form_data']['service_type'],
            'get_data_from_report': self._get_data_from_report(
                data['form_data']),

        }
