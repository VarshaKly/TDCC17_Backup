# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    loan_line_id = fields.Many2one(
        'account.loan.line',
        readonly=True,
        ondelete='restrict',
    )
    loan_id = fields.Many2one(
        'account.loan',
        readonly=True,
        store=True,
        ondelete='restrict',
    )

    @api.multi
    def post(self):
        res = super().post()
        for record in self:
            if record.loan_line_id:
                record.loan_id = record.loan_line_id.loan_id
                # record.loan_line_id.check_move_amount()
                # record.loan_line_id.loan_id.compute_posted_lines()
                if record.loan_line_id.sr_number == record.loan_id.installment_number:
                    record.loan_id.state = 'done'
        return res
