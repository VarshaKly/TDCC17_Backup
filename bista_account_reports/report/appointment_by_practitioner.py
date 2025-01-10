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


class AccountReportSaleServiceType(models.AbstractModel):
    _name = 'report.bista_account_reports.appointment_by_practitioner'
    _description = 'TDCC Account Report for appointment by practitioner'

    def _get_data_from_report(self, data):
        dt1 = data['start_date']
        dt2 = data['end_date']
        where = "(select count(account_invoice.id)>=1 from account_invoice " \
                "where account_invoice.appointment_id=aa.id and " \
                "account_invoice.state!='cancel') " \
                "and aa.start_date::date >= '" + \
                dt1 + \
            "' and aa.start_date::date <= '" + dt2 + "'"
        if data['phy_id']:
            where += "and physician.id = '" + str(data['phy_id']) + "'"
        if data['code_id']:
            where += "and physician.physician_code_id = '" + \
                str(data['code_id']) + "'"

        query = """ select count(aa.id) as number,
                    physician.name as physician,
                    pc.name as code
                    from appointment_appointment aa
                    left join res_partner physician on
                    aa.physician_id = physician.id
                    left join physician_code pc
                    on physician.physician_code_id = pc.id  where  """ + \
                where + """
                    group by physician,code

                    """

#         with_phy_name_qry = """ select count(aa.id) as number,
#                          physician.name as physician,
#                        code.name as code
#                         from appointment_appointment aa
#                         left join res_partner physician on
#                         aa.physician_id = physician.id
#                         left join physician_code code on code.id in
#        (select res.physician_code_id from res_partner res  )
#                         """ + where + """ group by code, physician"""
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
        return "Appointments by Practitioner from %s to %s" % (
            dt_str, end_dt_str)

#      def _get_title(self, data):
#         new_st_dt = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
#         new_end_dt = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
#         dt_str = new_st_dt.strftime('%d-%m-%Y ')
#         end_dt_str = new_end_dt.strftime('%d-%m-%Y ')
#         return "Sales by Practitioner for the period \
#                  %s to %s" % (dt_str,end_dt_str)

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_report = self.env['ir.actions.report']._get_report_from_name(
            'bista_account_reports.appointment_by_practitioner')
        return {
            'doc_ids': self.ids,
            'docs': self,
            'get_title': self._get_title(data['form_data']),
            'doc_model': payment_report.model,
            'clients': data['form_data']['client_id'],
            'with_name': data['form_data']['with_name'],
            'get_data_from_report': self._get_data_from_report(
                data['form_data']),

        }
