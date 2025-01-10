# -*- encoding: utf-8 -*-
# dathttp://www.bistasolutions.com)
#
#
from odoo import models, api, _
from odoo.exceptions import Warning
from datetime import datetime


class AccountPaymentReportSaleSummary(models.AbstractModel):
    _name = 'report.bista_account_reports.sales_by_prititioner_summary'
    _description = 'TDCC Account Reports for Sales Summary'

    def _get_data_from_report(self, data):

        if data.get('report_type') == 'sales_by_practitioner':
            users_env = self.env['res.users']
            dt1 = data['start_date']
            dt2 = data['end_date']
            where = "where ai.type in ('out_invoice', 'out_refund') and \
                    ai.state not in ('draft', 'cancel') and \
                    ai.user_id is not NULL and \
                    ai.date_invoice::date >= '" + dt1 + \
                    "' and ai.date_invoice:: date <= '" + dt2 + "'"
            if data['phy_id']:
                user = users_env.search([('partner_id', '=', data['phy_id'])],
                                        limit=1)
                if user:
                    where += " and ai.user_id = " + str(user.id)
                else:
                    raise Warning(
                        _('There is no User linked to this physician'))
            query = """ select
                        phy.name as physician,
                        ai.type as invoice_type,
                        sum(ai.amount_total) as sales,
                        CASE WHEN ai.type = 'out_refund'
                            THEN sum(ai.amount_total)
                            ELSE sum(ai.amount_total)-sum(ai.residual)
                            END as receipt,
                        CASE WHEN ai.type = 'out_invoice'
                        THEN sum(ai.residual)
                        ELSE 0
                        END as balance
                        from
                        account_invoice ai
                        left join res_users rs on
                        ai.user_id = rs.id
                        left join res_partner phy on
                        rs.partner_id = phy.id
                         """ + where + """
                        group by ai.type, physician
                        order by physician
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
        return "Sales by Practitioner for the period \
                 %s to %s" % (dt_str, end_dt_str)

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_report = self.env['ir.actions.report']._get_report_from_name(
            'bista_account_reports.sales_by_prititioner_summary')
        return {
            'doc_ids': self.ids,
            'docs': self,
            'get_title': self._get_title(data['form_data']),
            'doc_model': payment_report.model,
            'clients': data['form_data']['client_id'],
            'get_data_from_report': self._get_data_from_report(
                data['form_data']),

        }
