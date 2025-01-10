# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#

from odoo import models, fields, api
import base64
import io
from datetime import timedelta

try:
    import xlwt
except ImportError:
    xlwt = None


class CashflowReportWizard(models.TransientModel):
    _name = 'cashflow.report.wizard'
    _description = 'Cash flow Report'

    start_date = fields.Date(string='Start Date',
                             default=fields.date.today())
    end_date = fields.Date(string='End Date',
                           default=fields.date.today())

    def group_by_salesperson(self):
        # query = """
        #             WITH TRANSACTION AS(
        #                 SELECT
        #                     inv.user_id as user_id,
        #                     usr.partner_id as partner_id,
        #                     TO_CHAR(aml.date_maturity::DATE, 'yyyy-mm-dd') AS date,
        #                     ROUND(sum(aml.debit), 2) AS target_in,
        #                     0.00 AS actual_in
        #                 FROM
        #                     account_move_line aml
        #                     LEFT JOIN account_invoice inv ON inv.id = aml.invoice_id
        #                     LEFT JOIN res_users usr ON usr.id = inv.user_id
        #                 WHERE
        #                     aml.date_maturity BETWEEN '%s' AND '%s'
        #                     AND inv.type in ('out_invoice','in_refund')
        #                     AND aml.invoice_id IS NOT NULL
        #                     AND aml.account_id = inv.account_id
        #                 GROUP BY
        #                     inv.user_id,
        #                     usr.partner_id,
        #                     aml.date_maturity,
        #                     inv.user_id
        #             UNION ALL
        #                 SELECT
        #                     NULL as user_id,
        #                     (CASE
        #                         WHEN payment.physician_type = 'single'
        #                         THEN payment.physician_id
        #                         ELSE app.physician_id
        #                     END) as partner_id,
        #                     TO_CHAR(payment.payment_date::DATE, 'yyyy-mm-dd') AS date,
        #                     0.00 AS target_in,
        #                     (CASE
        #                         WHEN payment.physician_type = 'single'
        #                         THEN sum(payment.amount)
        #                         ELSE sum(app.amount)
        #                     END) as actual_in
        #                 FROM
        #                     account_payment payment
        #                     LEFT JOIN account_payment_physician app ON app.payment_id = payment.id
        #                 WHERE
        #                     payment.payment_date BETWEEN '%s' AND '%s'
        #                     AND payment.payment_type = 'inbound'
        #                 GROUP BY
        #                     payment.physician_id,
        #                     app.physician_id,
        #                     payment.physician_type,
        #                     payment.payment_date)
        #             SELECT tr.partner_id as partner_id,
        #                    SUM(tr.target_in) AS target_in,
        #                    SUM(tr.actual_in) AS actual_in
        #             FROM
        #                 TRANSACTION tr
        #             GROUP BY
        #                 tr.partner_id""" % (self.start_date, self.end_date,
        #                                   self.start_date, self.end_date)
        query = """
                    WITH TRANSACTION AS(
                        SELECT
                            usr.id as user_id,
                            app.physician_id as partner_id,
                            TO_CHAR(app.start_date::DATE, 'yyyy-mm-dd')
                            AS date,
                            ROUND(sum(app.price_subtotal), 2) AS target_in,
                            0.00 AS actual_in
                        FROM
                            appointment_appointment app
                            LEFT JOIN res_users usr ON
                            app.physician_id=usr.partner_id
                        WHERE
                            app.start_date::DATE BETWEEN '%s' AND '%s'
                            AND app.state NOT IN ('cancelled', 'new')
                            AND app.price_subtotal > 0
                            AND app.physician_id is NOT NULL
                        GROUP BY
                            app.physician_id,
                            app.start_date::DATE,
                            usr.id
                    UNION ALL
                        SELECT
                            NULL as user_id,
                            (CASE
                                WHEN payment.physician_type = 'single'
                                THEN payment.physician_id
                                ELSE app.physician_id
                            END) as partner_id,
                            TO_CHAR(payment.payment_date::DATE, 'yyyy-mm-dd')
                            AS date,
                            0.00 AS target_in,
                            (CASE
                                WHEN payment.physician_type = 'single'
                                THEN sum(payment.amount)
                                ELSE sum(app.amount)
                            END) as actual_in
                        FROM
                            account_payment payment
                            LEFT JOIN account_payment_physician app
                            ON app.payment_id = payment.id
                        WHERE
                            payment.payment_date BETWEEN '%s' AND '%s'
                            AND payment.payment_type = 'inbound'
                        GROUP BY
                            payment.physician_id,
                            app.physician_id,
                            payment.physician_type,
                            payment.payment_date)
                    SELECT tr.partner_id as partner_id,
                           SUM(tr.target_in) AS target_in,
                           SUM(tr.actual_in) AS actual_in
                    FROM
                        TRANSACTION tr
                    GROUP BY
                        tr.partner_id""" % (self.start_date, self.end_date,
                                          self.start_date, self.end_date)
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    def group_by_date(self, start_date, end_date):
        # query = """
        #             WITH TRANSACTION AS
        #                 (SELECT inv.id AS invoice,
        #                       TO_CHAR(aml.date_maturity::DATE,'yyyy-mm-dd') AS date,
        #                       (CASE
        #                            WHEN inv.type IN ('out_invoice',
        #                                              'in_refund') THEN ROUND(sum(aml.debit), 2)
        #                            ELSE 0.00
        #                        END) AS target_in,
        #                       (CASE
        #                            WHEN inv.type IN ('in_invoice','out_refund')
        #                            THEN (ROUND(sum(aml.credit), 2))
        #                            ELSE 0.00
        #                        END) AS target_out,
        #                       0.00 AS actual_in,
        #                       0.00 AS actual_out
        #                 FROM account_move_line aml
        #                 LEFT JOIN account_invoice inv ON inv.id = aml.invoice_id
        #                 WHERE aml.date_maturity BETWEEN '%s' AND '%s'
        #                 AND aml.invoice_id IS NOT NULL
        #                 AND aml.account_id = inv.account_id
        #                 GROUP BY inv.id, aml.date_maturity
        #             UNION ALL
        #                 SELECT payment.id AS payment,
        #                     TO_CHAR(aml.date_maturity::DATE,'yyyy-mm-dd') AS date,
        #                     0.00 AS target_in,
        #                     0.00 AS target_out,
        #                     (CASE
        #                         WHEN payment.payment_type = 'inbound'
        #                         THEN ROUND(sum(aml.credit), 2)
        #                         ELSE 0.00
        #                     END) AS actual_in,
        #                     (CASE
        #                         WHEN payment.payment_type = 'outbound'
        #                         THEN (ROUND(sum(aml.debit), 2))
        #                         ELSE 0.00
        #                     END) AS actual_out
        #                FROM account_move_line aml
        #                LEFT JOIN account_invoice inv ON inv.id = aml.invoice_id
        #                LEFT JOIN account_payment payment ON payment.id = aml.payment_id
        #                WHERE payment.payment_date BETWEEN '%s' AND '%s'
        #                GROUP BY payment.id, aml.date_maturity
        #             UNION ALL
        #                SELECT voucher.id AS vno,
        #                     TO_CHAR(aml.date_maturity::DATE,'yyyy-mm-dd') AS date,
        #                     (CASE
        #                         WHEN voucher.voucher_type = 'sale'
        #                         THEN ROUND(sum(aml.debit), 2)
        #                         ELSE 0.00
        #                     END) AS target_in,
        #                     (CASE
        #                         WHEN voucher.voucher_type = 'purchase'
        #                         THEN ROUND(sum(aml.credit), 2)
        #                         ELSE 0.00
        #                     END) AS target_out,
        #                     (CASE
        #                         WHEN voucher.voucher_type = 'sale' and voucher.pay_now = 'pay_now'
        #                         THEN ROUND(sum(aml.debit), 2)
        #                         ELSE 0.00
        #                     END) AS actual_in,
        #                     (CASE
        #                         WHEN voucher.voucher_type = 'purchase' and voucher.pay_now = 'pay_now'
        #                         THEN ROUND(sum(aml.credit), 2)
        #                         ELSE 0.00
        #                     END) AS actual_out
        #                 FROM account_move_line aml
        #                 LEFT JOIN account_voucher voucher ON voucher.move_id = aml.move_id
        #                 WHERE aml.date_maturity BETWEEN '%s' AND '%s'
        #                 AND aml.account_id = voucher.account_id
        #                 GROUP BY aml.date_maturity,voucher.voucher_type, voucher.pay_now, voucher.id)
        #
        #             SELECT TO_CHAR(tr.date::DATE,'yyyy-mm-dd') AS date,
        #                    sum(tr.target_in) AS target_in,
        #                    sum(tr.target_out) AS target_out,
        #                    sum(tr.actual_in) as actual_in,
        #                    sum(tr.actual_out) as actual_out
        #             FROM TRANSACTION tr
        #             GROUP BY tr.date
        #             ORDER BY tr.date ASC """ % (start_date, end_date,
        #                                         start_date, end_date,
        #                                         start_date, end_date)

        query = """
                    WITH TRANSACTION AS
                        (SELECT app.id as appointment,
                            TO_CHAR(app.start_date::DATE, 'yyyy-mm-dd') AS date,
                            ROUND(sum(app.price_subtotal), 2) AS target_in,
                            0.00  AS target_out,
                            0.00 AS actual_in,
                            0.00 AS actual_out
                        FROM
                            appointment_appointment app
                        WHERE
                            app.start_date::DATE BETWEEN '%s' AND '%s'
                            AND app.state NOT IN ('cancelled', 'new')
                            AND app.price_subtotal > 0
                        GROUP BY
                            app.id,
                            app.start_date::DATE
                    UNION ALL
                        SELECT inv.id AS invoice,
                              TO_CHAR(aml.date_maturity::DATE,'yyyy-mm-dd') AS date,
                              0.00 AS target_in,
                              (CASE
                                   WHEN inv.type IN ('in_invoice','out_refund')
                                   THEN (ROUND(sum(aml.credit), 2))
                                   ELSE 0.00
                               END) AS target_out,
                              0.00 AS actual_in,
                              0.00 AS actual_out
                        FROM account_move_line aml
                        LEFT JOIN account_invoice inv ON inv.id = aml.invoice_id
                        WHERE aml.date_maturity BETWEEN '%s' AND '%s'
                        AND aml.invoice_id IS NOT NULL
                        AND aml.account_id = inv.account_id
                        GROUP BY inv.id, aml.date_maturity
                    UNION ALL
                        SELECT payment.id AS payment,
                            TO_CHAR(aml.date_maturity::DATE,'yyyy-mm-dd') AS date,
                            0.00 AS target_in,
                            0.00 AS target_out,
                            (CASE
                                WHEN payment.payment_type = 'inbound'
                                THEN ROUND(sum(aml.credit), 2)
                                ELSE 0.00
                            END) AS actual_in,
                            (CASE
                                WHEN payment.payment_type = 'outbound'
                                THEN (ROUND(sum(aml.debit), 2))
                                ELSE 0.00
                            END) AS actual_out
                       FROM account_move_line aml
                       LEFT JOIN account_invoice inv ON inv.id = aml.invoice_id
                       LEFT JOIN account_payment payment ON payment.id = aml.payment_id
                       WHERE payment.payment_date BETWEEN '%s' AND '%s'
                       GROUP BY payment.id, aml.date_maturity
                    UNION ALL
                       SELECT voucher.id AS vno,
                            TO_CHAR(aml.date_maturity::DATE,'yyyy-mm-dd') AS date,
                            (CASE
                                WHEN voucher.voucher_type = 'sale'
                                THEN ROUND(sum(aml.debit), 2)
                                ELSE 0.00
                            END) AS target_in,
                            (CASE
                                WHEN voucher.voucher_type = 'purchase'
                                THEN ROUND(sum(aml.credit), 2)
                                ELSE 0.00
                            END) AS target_out,
                            (CASE
                                WHEN voucher.voucher_type = 'sale' and voucher.pay_now = 'pay_now'
                                THEN ROUND(sum(aml.debit), 2)
                                ELSE 0.00
                            END) AS actual_in,
                            (CASE
                                WHEN voucher.voucher_type = 'purchase' and voucher.pay_now = 'pay_now'
                                THEN ROUND(sum(aml.credit), 2)
                                ELSE 0.00
                            END) AS actual_out
                        FROM account_move_line aml
                        LEFT JOIN account_voucher voucher ON voucher.move_id = aml.move_id
                        WHERE aml.date_maturity BETWEEN '%s' AND '%s'
                        AND aml.account_id = voucher.account_id
                        GROUP BY aml.date_maturity,voucher.voucher_type, voucher.pay_now, voucher.id)

                    SELECT TO_CHAR(tr.date::DATE,'yyyy-mm-dd') AS date,
                           sum(tr.target_in) AS target_in,
                           sum(tr.target_out) AS target_out,
                           sum(tr.actual_in) as actual_in,
                           sum(tr.actual_out) as actual_out
                    FROM TRANSACTION tr
                    GROUP BY tr.date
                    ORDER BY tr.date ASC """ % (start_date, end_date,
                                                start_date, end_date,
                                                start_date, end_date,
                                                start_date, end_date)
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    def write_line_data(self, row, worksheet, start_date, end_date):
        font = xlwt.Font()
        font.name = 'Calibri'
        font.height = 20 * 11
        style = xlwt.XFStyle()
        style.font = font
        style.num_format_str = '###0.00'
        query_data = self.group_by_date(start_date, end_date)
        if not query_data:
            data = {'target_in': 0.0, 'target_out': 0.00, 'actual_in': 0.0, 'actual_out': 0.00}
        else:
            data = query_data[0]
        target_column = 2
        actual_column = 6
        worksheet.write(row, target_column, data.get('target_in'), style)
        target_column += 1
        worksheet.write(row, target_column, data.get('target_out'), style)
        target_column += 1
        worksheet.write(row, actual_column, data.get('actual_in'), style)
        actual_column += 1
        worksheet.write(row, actual_column, data.get('actual_out'), style)
        actual_column += 1
        return data

    @api.multi
    def print_xls_report(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Cashflow Report', cell_overwrite_ok=True)
        style1 = xlwt.easyxf("font: bold on; alignment: horiz centre;")
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        font = xlwt.Font()
        font.name = 'Calibri'
        font.height = 20 * 11
        style = xlwt.XFStyle()
        style.font = font
        style.alignment = alignment
        start_date = self.start_date
        end_date = self.end_date
        total_day = end_date - start_date
        for i in range(0, 255):
            worksheet.col(i).width = 256 * 17
            worksheet.row(i).height = 300 * 1

        worksheet.write(1, 1, 'TARGET', style)
        worksheet.write(2, 2, 'IN', style)
        worksheet.write(2, 3, 'OUT', style)

        worksheet.write(1, 5, 'ACTUAL', style)
        worksheet.write(2, 6, 'IN', style)
        worksheet.write(2, 7, 'OUT', style)
        worksheet.write(1, 9, 'Salesperson', style)
        worksheet.write(2, 10, 'TARGET IN', style)
        worksheet.write(2, 11, 'ACTUAL IN', style)

        target_in_row = 3
        actual_in_row = 3
        style.num_format_str = 'dd/mm/yyyy'
        worksheet.set_panes_frozen(True)
        worksheet.set_horz_split_pos(3)
        row = 3
        target_in_total = target_out_total = actual_in_total = actual_out_total = 0.00

        # Write data in sheet : Group By Date
        for i in range(total_day.days + 1):
            worksheet.write(target_in_row, 1, start_date + timedelta(i), style)
            target_in_row += 1
            worksheet.write(actual_in_row, 5, start_date + timedelta(i), style)
            actual_in_row += 1
            data = self.write_line_data(row, worksheet, start_date + timedelta(i), start_date + timedelta(i))
            target_in_total += data.get('target_in')
            target_out_total += data.get('target_out')
            actual_in_total += data.get('actual_in')
            actual_out_total += data.get('actual_out')
            row += 1

        total_style_font = xlwt.Font()
        total_style_font.name = 'Calibri'
        total_style_font.height = 20 * 11
        total_style_font.bold = True
        total_style = xlwt.XFStyle()
        total_style.font = total_style_font
        total_style.num_format_str = '###0.00'
        worksheet.write(row, 2, target_in_total, total_style)
        worksheet.write(row, 3, target_out_total, total_style)
        worksheet.write(row, 6, actual_in_total, total_style)
        worksheet.write(row, 7, actual_out_total, total_style)

        # Write data in sheet : Group By Salesperson
        salesperson_data = self.group_by_salesperson()
        partner_obj = self.env['res.partner']
        sp_row = 3
        sp_font = xlwt.Font()
        sp_font.name = 'Calibri'
        sp_font.height = 20 * 11
        sp_style = xlwt.XFStyle()
        sp_style.font = font
        sp_style.num_format_str = '###0.00'
        sp_target_in_total = 0.00
        sp_actual_in_total = 0.00
        for data in salesperson_data:
            sp_column = 9
            if data.get('partner_id'):
                partner_id = partner_obj.browse(data.get('partner_id'))
                worksheet.write(sp_row, sp_column, partner_id.name, sp_style)
            else:
                worksheet.write(sp_row, sp_column, 'Undefined', sp_style)
            sp_column += 1
            worksheet.write(sp_row, sp_column, data.get('target_in') and float(data.get('target_in')) or 0.0, sp_style)
            sp_column += 1
            worksheet.write(sp_row, sp_column, data.get('actual_in') and float(data.get('actual_in')) or 0.0, sp_style)
            sp_row += 1
            sp_target_in_total += data.get('target_in') or 0.0
            sp_actual_in_total += data.get('actual_in') or 0.0

        worksheet.write(sp_row, 10, sp_target_in_total, total_style)
        worksheet.write(sp_row, 11, sp_actual_in_total, total_style)

        stream = io.BytesIO()
        workbook.save(stream)
        vals = {
            'cashflow_xls_output': base64.encodestring(stream.getvalue()),
            'name': 'Cash flow Report.xls'}
        attach_id = self.env['cashflow.report.print.link'].create(vals)

        return {
            'context': self.env.context,
            'name': 'Cashflow Report',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cashflow.report.print.link',
            'type': 'ir.actions.act_window',
            'res_id': attach_id.id,
            'target': 'new'
        }


class CashflowReportPrintLink(models.TransientModel):
    _name = 'cashflow.report.print.link'
    _description = 'Cash flow Report Link'

    cashflow_xls_output = fields.Binary(string='Excel Output')
    name = fields.Char(
        string='File Name',
        help='Save report as .xls format')
