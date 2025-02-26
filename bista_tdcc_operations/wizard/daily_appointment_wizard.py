# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class daily_appointment_wizard(models.TransientModel):
    _name = "daily.appointment.wizard"
    _description = 'Daily Appointment Wizard'

    client_id = fields.Many2one(comodel_name='res.partner',
                                string="Clients",
                                domain=[('is_student', '=',
                                         True)])
    clinic_id = fields.Many2one(comodel_name='res.company',
                                string="Clinic",
                                copy=False,
                                default=lambda self: self.env[
                                    'res.company']._company_default_get())
    physician_id = fields.Many2one(
        comodel_name='res.partner', domain=[
            ('is_physician', '=', True)])
    room_id = fields.Many2one(comodel_name='room.room', string="Room")
    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.context_today)
    end_date = fields.Date(
        string='End Date',
        default=fields.Date.context_today)
    print_pdf = fields.Boolean(string='Print', default=False)
    code_id = fields.Many2one('physician.code', string='Code')
    app_with_bal = fields.Boolean(string="Show negative balance", default=True)

    @api.onchange('start_date')
    def onchange_date(self):
        if self.start_date:
            self.end_date = self.start_date

    @api.multi
    def open_appointments(self):
        user_id = self.env.user
        practitionar_group = 'bista_tdcc_operations.group_tdcc_practitioner'
#        if self.physician_id and \
#            self.physician_id.id != user_id.partner_id.id and \
#            user_id.has_group(practitionar_group) and not user_id.has_group(
#                'bista_tdcc_operations.group_tdcc_all_appointments'):
#            raise Warning(_("You can see only own appointments"))
        if not self.print_pdf:
            domain = [('start_date', '>=', str(self.start_date)),
                      ('start_date', '<=', str(self.end_date)),
                      ('state', '!=', 'cancelled')]
            if self.code_id:
                physician_id = self.env['res.partner'].search(
                    [('physician_code_id', '=', self.code_id.id)])
                # if physician_id:
                domain += [('physician_id', 'in', physician_id.ids)]
            if self.physician_id and not self.code_id:
                domain += [('physician_id', '=', self.physician_id.id)]
            if self.clinic_id:
                domain += [('clinic_id', '=', self.clinic_id.id)]
            if self.room_id:
                domain += [('room_id', '=', self.room_id.id)]
            if not self.app_with_bal:
                domain += [('credit', '>', 0.00)]
            action = self.env.ref(
                'bista_tdcc_operations.daily_appointment_view_action').read()[0]
            action['domain'] = domain
            return action
        else:
            [data] = self.read()
            form_data = {
                'physician_id': self.physician_id.id,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'code_id': self.code_id.id,
                'clinic_id': self.clinic_id.id,
                'room_id': self.room_id.id
            }
            datas = {
                'ids': self._ids,
                'model': 'appointment.appointment',
                'form': data,
                'form_data': form_data
            }
            return self.env.ref(
                'bista_tdcc_operations.action_daily_appointment_report'
            ).report_action(self, data=datas)
