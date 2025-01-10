# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#
from odoo import models, api, _
from odoo.exceptions import Warning
from datetime import datetime


class AccountPaymentReport(models.AbstractModel):
    _name = 'report.bista_account_reports.report_bypaymentmethodsummary'
    _description = 'TDCC Account Reports'

    def _get_data_from_report(self, data):
        dt1 = data.get('start_date')
        dt2 = data.get('end_date')
        where = "ap.state != 'cancelled' and\
            ap.payment_type = 'inbound' and \
                      ap.payment_date::date >= '" + dt1 + \
                "' and ap.payment_date::date <= '" + dt2 + "'"
        if data.get('service_type_ids'):
                service_type_ids = data.get('service_type_ids')
                if len(service_type_ids) == 1:
                    where += " and ap.service_type_id = " + \
                        str(service_type_ids[0])
                elif len(service_type_ids) > 1:
                    where += " and ap.service_type_id in " + \
                        str(tuple(service_type_ids))
        if data.get('client_id'):
                where += " and ap.partner_id = " + str(data.get('client_id'))
        query = """select
                        sum(ap.amount) as amount,
                        aj.name as payment_method
                from account_payment ap
                        left join account_journal aj
                        on ap.journal_id=aj.id
                where
                    """ + where + """
                group by aj.name
                            """
        self._cr.execute(query)
        res = self._cr.dictfetchall()

        if not res:
            raise Warning(_("There is no data with selected options."))
        return res

    def _get_title(self, data):
        new_st_dt = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        new_end_dt = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        dt_str = new_st_dt.strftime('%d-%m-%Y ')
        end_dt_str = new_end_dt.strftime('%d-%m-%Y ')
        return "Receipts for the period %s to %s" % (dt_str, end_dt_str)

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_report = self.env['ir.actions.report']._get_report_from_name(
            'bista_account_reports.report_payment_method_summary')
        return {
            'doc_ids': self.ids,
            'docs': self,
            'get_title': self._get_title(data['form_data']),
            'doc_model': payment_report.model,
            'clients': data['form_data']['client_id'],
            'report_type': data['form_data']['report_type'],
            'get_data_from_report': self._get_data_from_report(
                data['form_data']),

        }
