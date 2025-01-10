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


class AccountReportAllocationPractitioner(models.AbstractModel):
    _name = 'report.bista_account_reports.allocation_by_practitioner'
    _description = 'TDCC Account Report for allocation by practitioner'

    def _get_data_from_report(self, data):
        dt1 = data['start_date']
        dt2 = data['end_date']
        utz = self.env.user.tz or 'UTC'
        where = """where
                        ap.physician_type = 'single' and
                        ap.state in ('posted', 'reconciled') and
                        (ap.payment_date AT TIME ZONE 'UTC'
                        AT TIME ZONE '%s') :: date >= '%s' and
                        (ap.payment_date AT TIME ZONE 'UTC'
                        AT TIME ZONE '%s') :: date <= '%s' and
                        ap.amount > 0 """ % (utz, dt1, utz, dt2)
        where1 = """where
                        ap.physician_type = 'multi' and
                        ap.state in ('posted', 'reconciled') and
                        (ap.payment_date AT TIME ZONE 'UTC'
                        AT TIME ZONE '%s') :: date >= '%s' and
                        (ap.payment_date AT TIME ZONE 'UTC'
                        AT TIME ZONE '%s') :: date <= '%s' and
                        ap.amount > 0 """ % (utz, dt1, utz, dt2)
        physician_ids = False
        if data['phy_id']:
            where += " and ap.physician_id = '" + str(data['phy_id']) + "'"
            where1 += " and app.physician_id = '" + str(data['phy_id']) + "'"
        elif data['code_id']:
            physician_ids = self.env['res.partner'].search(
                [('physician_code_id', '=', data['code_id'])])
            if len(physician_ids) == 1:
                where += " and ap.physician_id = '" + \
                    str(physician_ids[0].id) + "'"
                where1 += " and app.physician_id = '" + \
                    str(physician_ids[0].id) + "'"
            elif len(physician_ids) > 1:
                where += " and ap.physician_id in '%s'" % tuple(
                    physician_ids.ids)
                where1 += " and app.physician_id in '%s'" % tuple(
                    physician_ids.ids)
        query = """(select
                        TO_CHAR(ap.payment_date::DATE, 'dd/mm/yyyy') as date,
                        ap.name as id,
                        client.name as name,
                        physician.name as physician,
                        journal.name as journal_name,

                        ap.amount as total
                    from account_payment ap
                        left join res_partner client on
                        ap.partner_id = client.id
                        left join res_partner physician on
                        ap.physician_id = physician.id
                        left join account_journal journal on
                        ap.journal_id = journal.id
                    %s)
                    union all
                    (select
                        TO_CHAR(ap.payment_date::DATE, 'dd/mm/yyyy') as date,
                        ap.name as id,
                        client.name as name,
                        journal.name as journal_name,
                        physician.name as physician,
                        ap.amount as total
                    from account_payment ap
                        left join res_partner client on
                        ap.partner_id = client.id
                        left join account_journal journal on
                        ap.journal_id = journal.id
                        left join account_payment_physician app on
                        ap.id = app.payment_id
                        left join res_partner physician on
                        app.physician_id=physician.id
                    %s)
                    order by physician
                    """ % (where, where1)
        self._cr.execute(query)
        res = self._cr.dictfetchall()
#         query_code = """select name as physician_code
#                          from physician_code where id = (
#                          select rs.physician_code_id as idk
#                          from res_partner rs ,account_payment ap
#                          where rs.id = ap.physician_id)""
#    phy_with_code = """select py.id from
#     res_partner py where py.physician_code_id = (
#                             select id as id
#                             from physician_code where id = (
#                             select rs.physician_code_id as idk
#                             from res_partner rs ,account_payment ap
#                             where rs.id = ap.physician_id))"""

        if not res:
            raise Warning(_("There is no data with selected options."))
        return res

    def _get_title(self, data):
        new_st_dt = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        new_end_dt = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        dt_str = new_st_dt.strftime('%d-%m-%Y ')
        end_dt_str = new_end_dt.strftime('%d-%m-%Y ')
        return "Allocation by Practitioner for the Period  %s to %s" % (
            dt_str, end_dt_str)

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_report = self.env['ir.actions.report']._get_report_from_name(
            'bista_account_reports.allocation_by_practitioner')
        return {
            'doc_ids': self.ids,
            'docs': self,
            'with_name': data['form_data']['with_name'],
            'get_title': self._get_title(data['form_data']),
            'doc_model': payment_report.model,
            'clients': data['form_data']['client_id'],
            'get_data_from_report': self._get_data_from_report(
                data['form_data']),

        }
