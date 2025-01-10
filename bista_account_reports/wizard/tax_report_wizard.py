# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd Copyright (C) 2012 (http://www.bistasolutions.com)
#
#

from odoo import models, fields, api, _
from odoo.exceptions import Warning
import base64
import io
try:
    import xlwt
except ImportError:
    xlwt = None


class TaxReportWizard(models.TransientModel):
    _name = 'tax.report.wizard'
    _description = 'Account Report'

    start_date = fields.Date(string='Start Date',
                             default=fields.date.today())
    end_date = fields.Date(string='End Date',
                           default=fields.date.today())

    @api.multi
    def get_data(self):
        start_date = self.start_date
        end_date = self.end_date
        utz = self.env.user.tz or 'UTC'

        where1 = """ and vendor.vat <> '' and vendor.supplier = True"""
        where2 = """ and vendor.vat is NULL and vendor.supplier = True"""
        where3 = """ and vendor.customer = True and vendor.supplier = False """

        # Fetch data from invoices and vendor bills
        query = """ select
                            tax.name as accountname,
                            TO_CHAR(ai.date_invoice :: DATE, 'dd/mm/yyyy')
                            as invoicedate,
                            am.name as vno,
                            ai.reference as invno,
                            vendor.name as mainaccountname,
                            aa.code as acccode,
                            aa.name as accaame,
                            vendor.vat as trnno,
                            ai.vat_description as desciption,
                            ait.base as debit,
                            0.0 as credit,
                            ait.amount as taxamount

                        from account_invoice_tax ait
                            join account_invoice ai
                            on ait.invoice_id = ai.id
                            join res_partner vendor
                            on ai.partner_id = vendor.id
                            -- join account_invoice_line ail
                            -- on ail.invoice_id = ai.id
                            -- left join account_invoice_line_tax ailt
                            -- on ail.id=ailt.invoice_line_id
                            join account_move am
                            on ai.move_id = am.id
                            join account_account aa on
                            ait.account_id = aa.id
                            join account_tax tax on
                            ait.tax_id = tax.id 
                        where ai.state not in ('draft','cancel') and \
                        ai.date_invoice >= '%s' and
                        ai.date_invoice <= '%s' """ % (start_date, end_date)

        # Fetch data from Journal Items which are not linked to vendor bills
        # and having partner as supplier and originator tax is set
        aml_query = """select
                                    tax.name as accountname,
                                    TO_CHAR(aml.date_maturity :: DATE, 'dd/mm/yyyy')
                                    as invoicedate,
                                    am.name as vno,
                                    am.ref as invno,
                                    vendor.name as mainaccountname,
                                    aa.code as acccode,
                                    aa.name as accaame,
                                    vendor.vat as trnno,
                                    aml.name as desciption,
                                    (select sum(aml2.debit)
                                        from account_move_line_account_tax_rel amlt
                                        left join account_move_line aml2
                                        on amlt.account_move_line_id=aml2.id
                                        where aml2.move_id=am.id and
                                        amlt.account_tax_id=tax.id) as debit,
                                    0.0 as credit,
                                    aml.debit as taxamount
                            from account_move_line aml
                                    join res_partner vendor
                                    on aml.partner_id = vendor.id
                                    join account_move am
                                    on aml.move_id = am.id
                                    join account_account aa on
                                    aml.account_id = aa.id
                                    join account_tax tax on
                                    aml.tax_line_id = tax.id
                            where aml.tax_line_id is not null and
                                    aml.invoice_id is null and
                                    am.date >= '%s' and
                                    am.date <= '%s' and
                                    am.state = 'posted'
                """ % (start_date, end_date)

        # With TRN number vendor bill
        with_trn_qry = query + where1
        without_trn_qry = query + where2
        self._cr.execute(with_trn_qry)
        trn_res = self._cr.dictfetchall()
        self._cr.execute(without_trn_qry)
        without_trn_res = self._cr.dictfetchall()
        customer_qry = query + where3
        self._cr.execute(customer_qry)
        customer_res = self._cr.dictfetchall()

        # With TRN number Journal Items
        with_trn_aml = aml_query + where1
        self._cr.execute(with_trn_aml)
        trn_aml_res = self._cr.dictfetchall()
        # Merge data of with TRN from invoice and Journal Items
        trn_res += trn_aml_res
        # Without TRN number
        without_trn_aml = aml_query + where2
        self._cr.execute(without_trn_aml)
        without_trn_aml_res = self._cr.dictfetchall()
        # Merge data of without TRN from invoice and Journal Items
        without_trn_res += without_trn_aml_res

        # Fetch data from Journal items having no partner
        no_partner_aml = """select
                            tax.name as accountname,
                            TO_CHAR(aml.date_maturity :: DATE, 'dd/mm/yyyy')
                            as invoicedate,
                            am.name as vno,
                            am.ref as invno,
                            '' as mainaccountname,
                            aa.code as acccode,
                            aa.name as accaame,
                            '' as trnno,
                            aml.name as desciption,
                            (select sum(aml2.debit)
                            from account_move_line_account_tax_rel amlt
                            left join account_move_line aml2
                            on amlt.account_move_line_id=aml2.id
                            where aml2.move_id=am.id and
                            amlt.account_tax_id=tax.id) as debit,
                            0.0 as credit,
                            aml.debit as taxamount
                    from account_move_line aml
                            join account_move am
                            on aml.move_id = am.id
                            join account_account aa on
                            aml.account_id = aa.id
                            join account_tax tax on
                            aml.tax_line_id = tax.id
                    where aml.tax_line_id is not null and
                            aml.invoice_id is null and
                            am.date >= '%s' and
                            am.date <= '%s' and
                            am.state = 'posted' and
                            aml.partner_id is NULL
        """ % (start_date, end_date)
        self._cr.execute(no_partner_aml)
        no_partner_aml_res = self._cr.dictfetchall()
        without_trn_res += no_partner_aml_res
        if not (trn_res or without_trn_res or customer_res):
            raise Warning(_("There is no data with selected options."))
        else:
            return trn_res, without_trn_res, customer_res
    @api.multi
    def print_pdf_report(self):
        self.ensure_one()
        [data] = self.read()
        form_data = list(self.get_data())
        datas = {
            'ids': self._ids,
            'model': 'account.invoice.tax',
            'form': data,
            'form_data': form_data
        }
        return self.env.ref(
            'bista_account_reports.action_vat_report'
        ).report_action(self, data=datas)

    @api.multi
    def print_xls_report(self):

        workbook = xlwt.Workbook()

        worksheet = workbook.add_sheet('Vat Report', cell_overwrite_ok=True)
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['pale_blue']
        data_style = xlwt.easyxf("alignment: horiz centre;")
        style = xlwt.easyxf("font: bold on; alignment: horiz centre;")
        style.pattern = pattern
        for i in range(11):
            worksheet.col(i).width = 18 * 256
        row = 0
        col = 0
        worksheet.write(row, col, 'VNo', style)
        col += 1
        worksheet.write(row, col, 'Inv No', style)
        col += 1
        worksheet.write(row, col, 'Date', style)
        col += 1
        worksheet.write(row, col, 'AccountName', style)
        col += 1
        worksheet.write(row, col, 'TRN No', style)
        col += 1
        worksheet.write(row, col, 'Description', style)
        col += 1
        worksheet.write(row, col, 'Vat Amount', style)
        col += 1
        worksheet.write(row, col, 'TaxAmt', style)
        col += 1
        worksheet.write(row, col, 'TotalAmt', style)
        row = row + 2
        tb_title = 'Input Vat'
        worksheet.write(row, 0, tb_title, style)

        data = list(self.get_data())
        trn_data = self.get_data()[0]
        without_trn_data = self.get_data()[1]
        customer_data = self.get_data()[2]
        row = row + 1
        input_vat_total = 0.0
        input_tax = 0.0
        input_total = 0.0
        for rec in trn_data:
            row = row + 1
            col = 0
            acc_name = rec.get('accountname')
            eff_date = rec.get('invoicedate')
            vno = rec.get('vno')
            inv_no = rec.get('invno')
            main_acc_name = rec.get('mainaccountname')
            trn_no = rec.get('trnno')
            description = rec.get('desciption')
            debit = rec.get('debit')
            taxamount = rec.get('taxamount')
            worksheet.write(row, col, vno, data_style)
            col += 1
            worksheet.write(row, col, inv_no, data_style)
            col += 1
            worksheet.write(row, col, eff_date, data_style)
            col += 1
            worksheet.write(row, col, main_acc_name, data_style)
            col += 1
            worksheet.write(row, col, trn_no, data_style)
            col += 1
            worksheet.write(row, col, description, data_style)
            col += 1
            worksheet.write(row, col, debit, data_style)
            input_vat_total += debit
            col += 1
            worksheet.write(row, col, taxamount, data_style)
            input_tax += taxamount
            col += 1
            if not debit:
                worksheet.write(row, col, taxamount, data_style)
            else:
                worksheet.write(row, col, debit + taxamount, data_style)
        worksheet.write(row + 1, 5, 'Net Total', style)
        worksheet.write(row + 1, 6, input_vat_total, style)
        worksheet.write(row + 1, 7, input_tax, style)
        worksheet.write(row + 1, 8, input_vat_total + input_tax, style)
        row = row + 2
        output_title = 'Output Vat'
        worksheet.write(row, 0, output_title, style)
        output_vat_total = 0.0
        output_tax = 0.0
        for rec in customer_data:
            row = row + 1
            col = 0
            acc_name = rec.get('accountname')
            eff_date = rec.get('invoicedate')
            vno = rec.get('vno')
            inv_no = rec.get('invno')
            main_acc_name = rec.get('mainaccountname')
            trn_no = rec.get('trnno')
            description = rec.get('desciption')
            debit = rec.get('debit')
            taxamount = rec.get('taxamount')
            worksheet.write(row, col, vno, data_style)
            col += 1
            worksheet.write(row, col, inv_no, data_style)
            col += 1
            worksheet.write(row, col, eff_date, data_style)
            col += 1
            worksheet.write(row, col, main_acc_name, data_style)
            col += 1
            worksheet.write(row, col, trn_no, data_style)
            col += 1
            worksheet.write(row, col, description, data_style)
            col += 1
            worksheet.write(row, col, debit, data_style)
            output_vat_total += debit
            col += 1
            worksheet.write(row, col, taxamount, data_style)
            output_tax += taxamount
            col += 1
            if not debit:
                worksheet.write(row, col, taxamount, data_style)
            else:
                worksheet.write(row, col, debit + taxamount, data_style)
        worksheet.write(row + 1, 5, 'Net Total', style)
        worksheet.write(row + 1, 6, output_vat_total, style)
        worksheet.write(row + 1, 7, output_tax, style)
        worksheet.write(row + 1, 8, output_vat_total + output_tax, style)
        row = row + 2
        vat_title = 'VAT Non-Refundable Expense'
        worksheet.write(row, 0, vat_title, style)
        not_vat_total = 0.0
        not_vat_tax = 0.0
        for rec in without_trn_data:
            row = row + 1
            col = 0
            acc_name = rec.get('accountname')
            eff_date = rec.get('invoicedate')
            vno = rec.get('vno')
            inv_no = rec.get('invno')
            main_acc_name = rec.get('mainaccountname')
            trn_no = rec.get('trnno')
            description = rec.get('desciption')
            debit = rec.get('debit')
            taxamount = rec.get('taxamount')
            worksheet.write(row, col, vno, data_style)
            col += 1
            worksheet.write(row, col, inv_no, data_style)
            col += 1
            worksheet.write(row, col, eff_date, data_style)
            col += 1
            worksheet.write(row, col, main_acc_name, data_style)
            col += 1
            worksheet.write(row, col, trn_no, data_style)
            col += 1
            worksheet.write(row, col, description, data_style)
            col += 1
            worksheet.write(row, col, debit, data_style)
            if not debit:
                not_vat_total += 0
                #raise Warning(vno+":Debit "+debit+" Credit"+credit)
            else:
                not_vat_total += debit
            col += 1
            worksheet.write(row, col, taxamount, data_style)
            not_vat_tax += taxamount
            col += 1
            if not debit:
                worksheet.write(row, col, taxamount, data_style)
            else:
                worksheet.write(row, col, debit + taxamount, data_style)

        worksheet.write(row + 1, 5, 'Net Total', style)
        worksheet.write(row + 1, 6, not_vat_total, style)
        worksheet.write(row + 1, 7, not_vat_tax, style)
        worksheet.write(row + 1, 8, not_vat_total + not_vat_tax, style)
        stream = io.BytesIO()
        workbook.save(stream)
        vals = {
            'tax_xls_output': base64.encodestring(stream.getvalue()),
            'name': 'VAT Report.xls'}
        attach_id = self.env['tax.report.print.link'].create(vals)

        return {
            'context': self.env.context,
            'name': 'Vat Report',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tax.report.print.link',
            'type': 'ir.actions.act_window',
            'res_id': attach_id.id,
            'target': 'new'
        }


class TaxReportPrintLink(models.TransientModel):
    _name = 'tax.report.print.link'
    _description = 'TaxReport Link'

    tax_xls_output = fields.Binary(string='Excel Output')
    name = fields.Char(
        string='File Name',
        help='Save report as .xls format')
