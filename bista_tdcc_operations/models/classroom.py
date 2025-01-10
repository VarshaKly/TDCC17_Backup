# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#

from odoo import models, fields, api


class SchoolClass(models.Model):
    _name = 'school.class'
    _description = 'School Class'

    name = fields.Char(string="Name")
    clinic_id = fields.Many2one(comodel_name='res.company',
                                string='Clinic',
                                copy=False,
                                default=lambda self: self.env[
                                    'res.company']._company_default_get())
    active = fields.Boolean(string="Active", default=True)



class Classroom(models.Model):
    _name = 'school.classroom'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Class Room'

    name = fields.Char(string="Name")
    clinic_id = fields.Many2one(comodel_name='res.company',
                                string='Clinic',
                                copy=False,
                                default=lambda self: self.env[
                                    'res.company']._company_default_get())
    active = fields.Boolean(string="Active", default=True)
    class_id = fields.Many2one(comodel_name='school.class',
                               string='Room')
    staff_ids = fields.Many2many(comodel_name="res.partner",
                                 relation="classroom_staff_rel",
                                 column1="classroom_id",
                                 column2="staff_id",
                                 string="Staff")
    student_ids = fields.Many2many(comodel_name="res.partner",
                                   relation="classroom_student_rel",
                                   column1="classroom_id",
                                   column2="student_id",
                                   string="Student")
    term_id = fields.Many2one(comodel_name='academic.term',
                              string='Term')
    class_attendance_count = fields.Integer(string="Attendance",
                                         compute="_compute_class_attendance")
    
    @api.depends()
    def _compute_class_attendance(self):
        attendance_obj = self.env['attendance.attendance']
        for rec in self:
            domain = [('classroom_id', '=', rec.id)]
            attendance_count = attendance_obj.search_count(domain)
            rec.class_attendance_count = attendance_count

    @api.multi
    def name_get(self):
        result = []
        for classroom in self:
            name = classroom.name
            name += ' - ' + classroom.class_id.name
            name += ' - ' + classroom.term_id.name
            result.append((classroom.id, name))
        return result
    
    @api.multi
    def open_attendance(self):
        attendance_obj = self.env['attendance.attendance']
        attendance_action = 'bista_tdcc_operations.attendance_action_tdcc'
        action = self.env.ref(attendance_action).read()[0]
        for rec in self:
            domain = [('classroom_id', '=', rec.id)]
            attendance = attendance_obj.search(domain)
            if not attendance:
                return False
            if len(attendance) > 1:
                action['domain'] = [('id', 'in', attendance.ids)]
            elif attendance:
                form_attendance = 'bista_tdcc_operations.attendance_form_view_tdcc'
                attendance_form = (self.env.ref(form_attendance).id, 'form')
                action['views'] = [attendance_form]
                action['res_id'] = attendance.id
        return action
