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


class AccountPaymentReportSale(models.AbstractModel):
    _name = 'report.bista_account_reports.sales_by_prititioner_detail'
    _description = 'TDCC Account Reports for Sales'

    def _get_data_from_report(self, data):
        users_env = self.env['res.users']
        dt1 = data['start_date']
        dt2 = data['end_date']
        where = "where ai.type in ('out_invoice', 'out_refund') and \
                ai.state not in ('draft', 'cancel') and \
                     ai.user_id is not NULL and \
                     ai.date_invoice::date >= '" + dt1 + \
            "' and ai.date_invoice::date <= '" + dt2 + "'"
        if data['phy_id']:
            user = users_env.search([('partner_id', '=', data['phy_id'])],
                                    limit=1)
            if user:
                where += " and ai.user_id = " + str(user.id)
            else:
                raise Warning(_('There is no User linked to this physician'))
#             if data['code_id']:
#                 where += " and mpc.id = " + str(data['code_id'])
#
        query = """select TO_CHAR(ai.date_invoice::DATE, 'dd/mm/yyyy') as date,
                            ai.number as id,
                            st.name as service,
                            par.name as physician,
                            client.name as client_name,
                            company.name as clinic,
                            ail.price_total as total,
                            ai.type as invoice_type,
                            ail.price_total as receipt,
                            CASE WHEN ai.type = 'out_invoice'
                            THEN ai.residual
                            ELSE 0
                            END as balance
                           FROM account_invoice ai
                            left join appointment_appointment aa on
                            ai.appointment_id = aa.id
                            left join res_partner client on
                            ai.partner_id= client.id
                            left join res_users physician on
                            physician.id = ai.user_id
                            left join account_invoice_line ail on
                            ail.invoice_id = ai.id
                            left join service_type st on
                            ail.service_type_id = st.id
                            left join res_users res on
                            res.id = ai.user_id
                            left join res_partner par on
                            par.id = res.partner_id
                            left join physician_code code on
                            par.physician_code_id = code.id
                            left join res_company company on
                            ai.company_id = company.id
                             """ + where + """ ORDER BY ai.date_invoice """
        self._cr.execute(query)
        res = self._cr.dictfetchall()
        if not res:
            raise Warning(_("There is no data with selected options."))
        query1 = """select sum(j.due) as balance from(
        select sum(distinct i.balance) as due from (%s)  as i
        where i.balance > 0
        group by i.id) as j
        """ % query
        self._cr.execute(query1)
        res1 = self._cr.dictfetchone()
        balance = res1.get('balance') or 0
        return {'res': res, 'balance': balance}

    def _get_title(self, data):
        new_st_dt = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        new_end_dt = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        dt_str = new_st_dt.strftime('%d-%m-%Y ')
        end_dt_str = new_end_dt.strftime('%d-%m-%Y ')
        return "Sales by Practitioner for the period \
                 %s to %s" % (dt_str, end_dt_str)

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_report = self.env['ir.actions.report']._get_report_from_name(
            'bista_account_reports.sales_by_prititioner_detail')
        return {
            'doc_ids': self.ids,
            'docs': self,
            'get_title': self._get_title(data['form_data']),
            'doc_model': payment_report.model,
            'clients': data['form_data']['client_id'],
            'get_data_from_report': self._get_data_from_report(
                data['form_data']),

        }
