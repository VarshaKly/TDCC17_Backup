# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#
from odoo import models, api, _
from odoo.exceptions import Warning


class AccountReportSaleServiceType(models.AbstractModel):
    _name = 'report.bista_account_reports.sales_by_service_type'
    _description = 'TDCC Account Reports for Sales by Service Type'

    def _get_data_from_report(self, data):
        dt1 = data['start_date']
        dt2 = data['end_date']
        where = "ai.state not in ('cancel','draft') and \
                     ai.date_invoice::date >= '" + dt1 + \
                "' and ai.date_invoice::date <= '" + dt2 + "'"
        if data.get('service_type_id'):
                where += " and ail.service_type_id = " + \
                    str(data['service_type_id'])
        query = """select
                        to_char(ai.date_invoice, 'DD/MM/YYYY') as date,
                        ai.number as number,
                        tt.id as service_type_id,
                        rp.name as partner_name,
                        ai.type as invoice_type,
                        tt.name as treatment_name,
                        ail.price_subtotal as sales
                  from
                        account_invoice ai
                        left join account_invoice_line ail on
                        ai.id=ail.invoice_id
                        left join res_partner rp on rp.id=ai.partner_id
                        left join service_type tt on tt.id=ail.service_type_id
                            where """ + where

        self._cr.execute(query)
        res = self._cr.dictfetchall()

        if not res:
            raise Warning(_("There is no data with selected options."))
        result = {}
        for each in res:
            if each['service_type_id'] not in result:
                result.update({each['service_type_id']: []})
            result[each['service_type_id']].append(each)
        return result

    def _get_title(self, data):
        return "Sales by  Service Type for the period %s to %s" % (
            data.get('start_date'),
            data.get('end_date'))

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_report = self.env['ir.actions.report']._get_report_from_name(
            'bista_account_reports.sales_by_service_type')
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
