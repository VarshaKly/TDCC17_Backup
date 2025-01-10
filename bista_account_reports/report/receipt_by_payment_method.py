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
    _name = 'report.bista_account_reports.report_bypaymentmethod'
    _description = 'TDCC Account Reports'

    def _get_data_from_report(self, data):
        dt1 = data.get('start_date')
        dt2 = data.get('end_date')
        where = "ap.payment_type = 'inbound' and ap.state != 'cancelled' and \
                ap.payment_date >='" + \
            dt1 + "' and ap.payment_date <='" + dt2 + "'"
        if data.get('client_id'):
            where += " and ap.partner_id=%s" % (data.get('client_id'))
        if data.get('service_type_ids'):
            service_type_ids = data.get('service_type_ids')
            if len(service_type_ids) == 1:
                where += " and ap.service_type_id = " + \
                    str(service_type_ids[0])
            elif len(service_type_ids) > 1:
                where += " and ap.service_type_id in " + \
                    str(tuple(service_type_ids))
        query = """select
                    aj.id as payment_method_id,
                    ap.name as receipt_number,
                    ap.name as receipt_number,
                    rp.name as client_name,
                    case
                        when aj.code = 'PDC'
                        then TO_CHAR(ap.cheque_date::DATE, 'dd/mm/yyyy')
                        else TO_CHAR(ap.payment_date::DATE, 'dd/mm/yyyy')
                    end as payment_date,
                    aj.name as payment_method,
                    ap.amount as amount
                from account_payment ap
                    left join account_journal aj
                    on ap.journal_id=aj.id
                    left join res_partner rp
                    on ap.partner_id = rp.id

                where """ + where + """ order by payment_method """

        self._cr.execute(query)
        res = self._cr.dictfetchall()
        if not res:
            raise Warning(_("There is no data with selected options."))

        result = {}
        for each in res:
            if each['payment_method_id'] not in result:
                result.update({each['payment_method_id']: []})
            result[each['payment_method_id']].append(each)
        return result

    def _get_title(self, data):
        new_st_dt = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        new_end_dt = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        dt_str = new_st_dt.strftime('%d-%m-%Y ')
        end_dt_str = new_end_dt.strftime('%d-%m-%Y ')
        if data.get('client'):
            return "Receipts for %s from %s to %s" % (data.get('client'),
                                                      dt_str, end_dt_str)
        else:
            return "Receipts from %s to %s" % (dt_str, end_dt_str)

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_report = self.env['ir.actions.report']._get_report_from_name(
            'bista_account_reports.report_by_paymentmethod')
        return {
            'doc_ids': self.ids,
            'docs': self,
            'get_title': self._get_title(data['form_data']),
            'doc_model': payment_report.model,
            'clients': data['form_data']['client_id'],
            'client_name': data['form_data']['client'],
            'report_type': data['form_data']['report_type'],
            'get_data_from_report': self._get_data_from_report(
                data['form_data']),

        }
