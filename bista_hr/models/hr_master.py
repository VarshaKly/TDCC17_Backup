# -*- encoding: utf-8 -*-
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
#

from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError
from lxml import etree


class Partner(models.Model):
    _inherit = 'res.partner'

    is_employee = fields.Boolean("Is an Employee")
    unique_no = fields.Char(string="Unique ID", default="New", readonly=True)

    @api.model
    def create(self, vals):
        vals['unique_no'] = self.env['ir.sequence'].next_by_code('res.partner.sequence')
        return super(Partner, self).create(vals)

    def update_sequence(self):
        active_ids = self.env.context.get('active_ids')
        contacts = self.env['res.partner'].browse(active_ids).filtered(lambda x: x.unique_no == 'New').sorted(key=lambda r: r.id)
        for c in contacts:
            c.unique_no = self.env['ir.sequence'].next_by_code('res.partner.sequence')

    @api.model
    def _fields_view_get_address(self, arch):
        # overwrite base method to display city_id and invisible city field.
        doc = etree.fromstring(arch)
        if doc.xpath("//field[@name='city_id']"):
            return arch
        for city_node in doc.xpath("//field[@name='city']"):
            replacement_xml = """
                <div>
                    <field name="country_enforce_cities" invisible="1"/>
                    <field name='city' placeholder="%s" invisible="1"/>
                    <field name='city_id' placeholder="%s" context="{
                    'country_id': country_id}"
                    />
                </div>
                """ % (_('City'), _('City'))
            city_id_node = etree.fromstring(replacement_xml)
            city_node.getparent().replace(city_node, city_id_node)

        arch = etree.tostring(doc, encoding='unicode')
        return arch

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            return {'domain': {
                'state_id': [('country_id', '=', self.country_id.id)],
                'city_id': [('country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': [], 'city_id': []}}

    @api.onchange('city_id')
    def _onchange_city_id(self):
        self.city = self.city_id.name
        self.zip = self.city_id.zipcode
        self.state_id = self.city_id.state_id
        self.country_id = self.city_id.country_id


class Employee(models.Model):
    _inherit = 'hr.employee'

    def _get_is_create_user(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.get_param('bista_hr.is_create_user')
        return ICPSudo.get_param('bista_hr.is_create_user')

    @api.model
    def default_get(self, default_fields):
        res = super(Employee, self).default_get(default_fields)
#         if self._get_is_create_user():
#             res['is_create_user'] = True
        if self.env.user.company_id and \
                self.env.user.company_id.partner_id.city_id:
            res[
                'work_location'] = self.env.user.company_id.partner_id.city_id.id
        return res

#     @api.model
#     def create(self, vals):
#         obj_res_users = self.env['res.users']
#         template_obj = self.env['mail.template']
#         ir_model_obj = self.env['ir.model.data']
#         obj_job = self.env['hr.job']
#         if vals.get('work_email', False):
#             if not validate_email(vals.get('work_email', False)):
#                 raise ValidationError(_('Email address you\
#                  specified is not valid'))
# if not self._get_is_create_user():
# """If is create user not enable in HR configuration then it will\
# not create user or send mail to user. Only normal employee\
# creation flow executed"""
# Here Code is placed from bista_hr_gratuity module to set partner
# if vals.get('user_id'):
# user = self.env['res.users'].browse(vals.get('user_id'))
# vals.update({'partner_id': user.partner_id.id})
# else:
# partner_obj = self.env['res.partner']
# partner_vals = {'name': vals.get('name'),
# 'ref': vals.get('emp_id') or '',
# 'customer': False,
# 'supplier': False,
# }
# partner_record = partner_obj.create(partner_vals)
# vals.update({'partner_id': partner_record.id,
# 'address_home_id': partner_record.id or False})
# res = super(Employee, self).create(vals)
# return res
#
#         if vals.get('user_id', False):
#             user_id = obj_res_users.browse(vals.get('user_id', False))
#             vals.update({
#                 'address_home_id':
#                     user_id and user_id.partner_id and user_id.partner_id.id,
#                 'partner_id': user_id.partner_id.id,
#             })
#         else:
#             user_id = obj_res_users.create({
#                 'name': vals.get('name'),
#                 'login': vals.get('work_email'),
#                 'email': vals.get('work_email')
#             })
#             vals.update({
#                 'user_id': user_id and user_id.id,
#                 'address_home_id':
#                     user_id and user_id.partner_id and user_id.partner_id.id,
#                 'partner_id': user_id.partner_id.id,
#             })
#         if vals.get('job_id', False):
#             obj_job.browse(vals.get('job_id')).groups_ids.write({
#                 'users': [(4, user_id and user_id.id)]
#             })
#         if user_id.company_id.password:
#             user_id.write({
#                 'password':
#                     user_id.company_id.password
#             })
#             email_tmp = 'mail_template_employee_login_credentials'
#             template_id = ir_model_obj.get_object_reference('bista_hr',
# email_tmp)[1]
#         res = super(Employee, self).create(vals)
# if res and res.bank_account_id:
# res.bank_account_id.partner_id = res.partner_id.id
# if template_id:
# template_rec = template_obj.browse(template_id)
# template_rec.send_mail(res.id, force_send=True)
# if not res.user_id:
# raise ValidationError(_("Please select Related User."))
#         return res
#
# For email verification and change in job_position, email, name
#     @api.multi
#     def write(self, vals):
#         res_user_obj = self.env['res.users']
#         job_obj = self.env['hr.job']
#         obj_res_group = self.env['res.groups']
# if not self._get_is_create_user():
# return super(Employee, self).write(vals)
#         for data in self:
#             if vals.get('work_email', False):
#                 if not validate_email(vals.get('work_email', False)):
#                     raise ValidationError(_('Email address you specified \
#                     is not valid'))
#             value = {}
#             if vals.get('name'):
#                 value.update({
#                     'name': vals.get('name')
#                 })
#             if vals.get('work_email'):
#                 value.update({
#                              'login': vals.get('work_email', False),
#                              'email': vals.get('work_email', False)
#                              })
#             if vals.get('user_id'):
#                 user_id = res_user_obj.browse(vals.get('user_id'))
#             else:
#                 user_id = data.user_id
#             user_id.write(value)
#             if user_id:
#                 if vals.get('job_id', False):
#                     job_id = data.job_id
#                     new_group_ids = \
#                         job_obj.browse(vals.get('job_id')).groups_ids.ids
#                     job_obj.browse(vals.get('job_id')).groups_ids.write({
#                         'users': [(4, user_id.id)]
#                     })
#                     if job_id:
#                         old_groups_ids = data.job_id.groups_ids.ids
#                         diff_groups_ids = list(set(old_groups_ids) -
#                                                set(new_group_ids))
#                         obj_res_group.browse(diff_groups_ids).write({
#                             'users': [(3, user_id.id)]
#                         })
#                 else:
#                     data.job_id.groups_ids.write({
#                         'users': [(4, user_id and user_id.id)]
#                     })
#         res = super(Employee, self).write(vals)
#         for each_data in self:
#             if not each_data.user_id:
#                 raise ValidationError(_("Please select Related User."))
#         return res

    # Computed Age Base On Birthday
    @api.one
    @api.depends('birthday')
    def compute_age(self):
        if self.birthday:
            calculated_date = relativedelta(datetime.today(), self.birthday)
            self.age = float(calculated_date.years)
        else:
            self.age = 0.0

    emp_id = fields.Char('Employee ID', copy=False)
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', default='single', groups=False)
    birthday = fields.Date('Date of Birth', groups=False)
    date_joining = fields.Date(string="Joining Date")
    date_employment = fields.Date(string="Employment Date")
    date_confirmation = fields.Date(string="Confirmation Date")
    date_marriage = fields.Date(string="Marriage Date")
    partner_permanent_address_id = fields.Many2one('res.partner',
                                                   string="Permanent Address")
    blood_group = fields.Selection([('o-', 'O-ve'), ('o+', 'O+ve'),
                                    ('a-', 'A-ve'), ('a+', 'A+ve'),
                                    ('b-', 'B-ve'), ('b+', 'B+ve'),
                                    ('ab-', 'AB-ve'), ('ab+', 'AB+ve')],
                                   string="Blood Group")
    age = fields.Float(compute=compute_age, string="Age")
    lang_ids = fields.One2many(
        'employee.language',
        'employee_id',
        string='Languages')
    id_skype = fields.Char(string="Skype ID")
    habit_ids = fields.Many2many('employee.habits', string="Habits")
    hobbies_ids = fields.Many2many('employee.hobbies', string="Hobbies")
    pf_account_no = fields.Char(string="PF Account No.")
    height = fields.Float(string="Height")
    weight = fields.Float(string="Weight")
    height_uom_id = fields.Many2one('uom.uom', string="UOM Height")
    weight_uom_id = fields.Many2one('uom.uom', string="UOM Weight")
    disability_ids = fields.Many2many('employee.disability',
                                      string="Disability")
    work_country_id = fields.Many2one('res.country', string="Work Country")
#    work_location = fields.Many2one('res.city', string="Work Location")
    region_id = fields.Many2one('res.country.group', string="Region")
    family_detail_ids = fields.One2many('hr.family', 'employee_id',
                                        string="Family Details")
    family_visa_detail_ids = fields.One2many('hr.family.visa', 'employee_id',
                                             string="Family Visa")
    document_ids = fields.One2many('hr.document', 'employee_id',
                                   string="Documents")
    qualification_ids = fields.One2many('hr.qualification', 'employee_id',
                                        string="Qualifications")
    visa_ids = fields.One2many('hr.visa', 'employee_id', string="Visa Details")
    insurance_ids = fields.One2many('hr.insurance', 'employee_id',
                                    string="Insurance Details")
    religion_id = fields.Many2one('hr.religion', 'Religion')
#     employee_code = fields.Char('Emp Code')
    is_create_user = fields.Boolean('Is create user?')
    name_arabic = fields.Char(string='Name Arabic', translate=True)
    partner_id = fields.Many2one('res.partner', 'Partner',
                                 help='For gratuity employee.')
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    passport_issue_country = fields.Many2one('res.country',
                                             string="Passport Issue Country")
    is_new = fields.Boolean(string="Is New Employee?")
    passport_issue_date = fields.Date(string="Passport Issue Date")
    passport_expiry_date = fields.Date(string="Passport Expiry Date")
    father_name = fields.Char(string="Father Name")
    mother_name = fields.Char(string="Mother Name")
    emergency_contact1 = fields.Char(string="Emergency Contact1")
    emergency_street1 = fields.Char(string="Emergency  Street1")
    emergency_city1 = fields.Char(string="Emergency City1")
    emergency_country1 = fields.Many2one('res.country',
                                         string="Emergency Country1")
    emergency_zip1 = fields.Char(string="Emergency Zip1")
    emergency_phone1 = fields.Char(string="Emergency Phone1")
    emergency_mobile1 = fields.Char(string="Emergency Mobile1")
    emergency_email1 = fields.Char(string="Emergency Email1")
    emergency_relation1 = fields.Char(string="Emergency Relation1")
    emergency_contact2 = fields.Char(string="Emergency Contact2")
    emergency_street2 = fields.Char(string="Emergency  Street2")
    emergency_city2 = fields.Char(string="Emergency City2")
    emergency_country2 = fields.Many2one('res.country',
                                         string="Emergency Country2")
    emergency_zip2 = fields.Char(string="Emergency Zip2")
    emergency_phone2 = fields.Char(string="Emergency Phone2")
    emergency_mobile2 = fields.Char(string="Emergency Mobile2")
    emergency_relation2 = fields.Char(string="Emergency Relation2")
    emergency_email2 = fields.Char(string="Emergency Email2")
    identification_expiry_date = fields.Date(string='Emirates Expiry date')

    _sql_constraints = [
        ('unique_emp_id', 'unique (emp_id)', 'Employee ID already exists!')]

    @api.onchange('work_country_id')
    def onchange_work_country_id(self):
        for country in self.work_country_id:
            cntry_grp_obj = self.env['res.country.group']
            cntry_grp_id = cntry_grp_obj.search(
                [('country_ids', 'in', country.id)])
            if country.id and cntry_grp_id.id:
                self.region_id = cntry_grp_id.id

    @api.onchange('address_id')
    def _onchange_address(self):
        res = super(Employee, self)._onchange_address()
        if self.address_id:
            self.work_location = self.address_id.city_id.id
        return res

    @api.onchange('first_name', 'last_name')
    def onchange_emp_first_last_name(self):
        if self.first_name and not self.last_name:
            self.name = self.first_name
        elif not self.first_name and self.last_name:
            self.name = self.last_name
        elif self.first_name and self.last_name:
            self.name = self.first_name + " " + self.last_name
        else:
            self.name = ""

    @api.multi
    def get_employeement_docs(self):
        '''
        Get employment related docs
        :return:
        '''
        self.ensure_one()
        document = self.env['applicant.hr.document'].search(
            [('employee_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': _('Employment Document'),
            'res_model': 'applicant.hr.document',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', document.ids)],
            'res_id': document.ids,
            'target': 'current',
        }

    @api.multi
    def on_smart_button_click(self):
        self.ensure_one()
        context = dict(self._context)
        action = self.env.ref(context.get('action_id'))
        if context.get(
                'action_id') == "account_asset.action_account_asset_asset_form":
            domain = [('employee_id', '=', self.id)]
        elif context.get('action_id') == "bista_hr.action_hr_insurance":
            domain = [('employee_id', '=', self.id)]
            context['default_employee_id'] = self.id
            context['emp_name'] = self.name
        else:
            domain = [('employee_id', '=', self.id)]
            context['default_employee_id'] = self.id
        return self.generate_result(action, context, domain)

    def generate_result(self, action, context, domain):
        result = {
            'name': action.name,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': context,
            'res_model': action.res_model,
            'domain': domain,
        }
        return result


class RePartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.model
    def default_get(self, fields_list):
        res = super(RePartnerBank, self).default_get(fields_list)
        emp_id = self._context.get('emp_id')
        if emp_id:
            emp_id = self.env['hr.employee'].browse(emp_id)
            res['partner_id'] = emp_id.partner_id.id or False
        return res


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    @api.multi
    def create_employee_from_applicant(self):
        """ Write employee id from the res_id """
        res = super(HrApplicant, self).create_employee_from_applicant()
        if res.get('res_id', False):
            self.hr_document_ids.write({'employee_id': res['res_id']})
        return res


class HrFamily(models.Model):
    _name = 'hr.family'
    _description = "Employee Family Details"

    name = fields.Char(string="Name", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    family_relation_id = fields.Many2one('hr.family.relation',
                                         string="Relation")
    contact_no = fields.Char(string="Contact No.")
    partner_address_id = fields.Text(string="Address")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class HrFamilyRelation(models.Model):
    _name = 'hr.family.relation'
    _description = "Employee Family Relation"

    name = fields.Char(string="Name")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class HrFamilyVisa(models.Model):
    _name = 'hr.family.visa'
    _description = "Employee Family Visa"

    name = fields.Char(string="Name", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    member_name = fields.Char(string="Applied For", required=True)
    family_relation_id = fields.Many2one('hr.family.relation',
                                         string="Relation")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    country_id = fields.Many2one('res.country', string="Country")
    status = fields.Selection([('applied', 'Applied'),
                               ('in progress', 'In Progress'),
                               ('approved', 'Approved'),
                               ('rejected', 'Rejected'),
                               ('expired', 'Expired')], string="Status")
    no_of_entry = fields.Integer(string="No. of Entry")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class HrDocument(models.Model):
    _name = 'hr.document'
    _description = "Employee Documents"
    _inherit = 'mail.thread'

    name = fields.Char(string="Name", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    file = fields.Binary(string="File")
    file_name = fields.Char('File Name')
    document_type_id = fields.Many2one('document.type', string='Document Type')
    date_start = fields.Date(string="Start Date")
    date_expiry = fields.Date(string="Expiry Date")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)
    status = fields.Selection([('ongoing', 'Ongoing'), ('expired', 'Expired')],
                              default='ongoing',
                              string="Status")


class DocumentType(models.Model):
    _name = 'document.type'
    _description = "Documents Type"

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)
    is_required = fields.Boolean(string='Required for Joining')


class HrQualification(models.Model):
    _name = 'hr.qualification'
    _description = "Education Qualification"

    name = fields.Char(string="Name", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    qualification_level_id = fields.Many2one('hr.qualification.level',
                                             string="Level")
    passing_year = fields.Integer(string="Passing Year")
    grade = fields.Char(string="Grade")
    document = fields.Binary(string="Document")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)

    @api.onchange('passing_year')
    def onchange_passing_year(self):
        year = datetime.now().year
        if self.passing_year:
            if self.passing_year < 1900 or self.passing_year > year:
                raise UserError("Passing Year Must Be Between Year 1900 to  %s"
                                % (year))


class HrQualificationLevel(models.Model):
    _name = 'hr.qualification.level'
    _description = "Education Qualification Level"

    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class EmployeeHabits(models.Model):
    _name = 'employee.habits'
    _description = "Employee Habits"

    name = fields.Char(string="Name")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class EmployeeHobbies(models.Model):
    _name = 'employee.hobbies'
    _description = "Employee Hobbies"

    name = fields.Char(string="Name")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class EmployeeDisability(models.Model):
    _name = 'employee.disability'
    _description = "Employee Disability"

    name = fields.Char(string="Name")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class HrVisa(models.Model):
    _name = 'hr.visa'
    _description = "Employee Visa"

    name = fields.Char(string="Description", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    country_id = fields.Many2one('res.country', string="Country")
    status = fields.Selection([('applied', 'Applied'),
                               ('in progress', 'In Progress'),
                               ('approved', 'Approved'),
                               ('rejected', 'Rejected'),
                               ('expired', 'Expired')], default='applied',
                              string="Status")
    no_of_entry = fields.Char(string="No. of Entries")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)
    type = fields.Selection([('employee', 'Employee'), ('family', 'Family')],
                            string="Type")
    family_member_id = fields.Many2one('hr.family', string="Family Member")
    family_relation_id = fields.Many2one(
        'hr.family.relation',
        string="Relation",
        related='family_member_id.family_relation_id')
    visa_type = fields.Selection([('sponsor', 'Sponsor'),
                                  ('dependent', 'Dependent')],
                                 string='Visa Type')


class HrInsuranceType(models.Model):
    _name = 'hr.insurance.type'
    _description = "Employee Insurance Type"

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class HrInsurance(models.Model):
    _name = 'hr.insurance'
    _description = "Employee Insurance"

    name = fields.Char('Description')
    type = fields.Selection([
        ('employee', 'Employee'),
        ('family', 'Family')],
        string="Contact Type", default='employee')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    family_relation_id = fields.Many2one('hr.family.relation', 'Relation')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    insurance_type = fields.Many2one('hr.insurance.type', 'Type')
    amount = fields.Float('Amount', help='For insurance amount')
    state = fields.Selection([('applied', 'Applied'),
                              ('in progress', 'In Progress'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected'),
                              ('expired', 'Expired')],
                             string="Status", default='applied')
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)
    family_id = fields.Many2one('hr.family', string='Family Member')

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'family':
            self.contact_name = ''
            self.family_id = False

    @api.onchange('family_id')
    def onchange_family_id(self):
        if self.family_id:
            self.family_relation_id = self.family_id.family_relation_id.id or \
                False


class EmployeeWorkLocation(models.Model):
    _name = 'employee.work.location'
    _description = "Work Location"

    name = fields.Char(string="Name")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class EmployeeLanguage(models.Model):
    _name = 'employee.language'
    _description = "Employee Language"
    _rec_name = 'language_id'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    language_id = fields.Many2one('language.language', string="Language")
    can_read = fields.Boolean('Can Read ?')
    can_write = fields.Boolean('Can Write ?')
    can_speak = fields.Boolean('Can Speak ?')
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class LanguageLanguage(models.Model):
    _name = 'language.language'
    _description = "Languages"

    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active')
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.user.company_id)


class HrReligion(models.Model):
    _name = 'hr.religion'
    _description = "Employee Religion"

    name = fields.Char(string="Name", required=True)


class ResCompany(models.Model):
    _inherit = 'res.company'

    password = fields.Char(string="Password", default='admin')
    city = fields.Many2one('res.city',
                           compute='_compute_address',
                           inverse='_inverse_city')

    # Overwrite base method to update city m2o field
    def _get_company_address_fields(self, partner):
        return {
            'street': partner.street,
            'street2': partner.street2,
            'city': partner.city_id.id,
            'zip': partner.zip,
            'state_id': partner.state_id,
            'country_id': partner.country_id,
        }

    # Overwrite base method to update city m2o field
    def _inverse_city(self):
        for company in self:
            company.partner_id.city_id = company.city.id


class HrJob(models.Model):
    _inherit = 'hr.job'

    groups_ids = fields.Many2many('res.groups', string="Groups")

    # Change in groups of Job Position
    @api.multi
    def write(self, vals):
        obj_employee = self.env['hr.employee']
        for data in self:
            employee_ids = obj_employee.search([('job_id', '=', data.id)])
            before_groups_ids = data.groups_ids
            res = super(HrJob, self).write(vals)
            if vals.get('groups_ids', False):
                groups_ids = data.groups_ids
                for each_emp_id in employee_ids:
                    if each_emp_id.user_id:
                        before_groups_ids.write({
                            'users': [(3, each_emp_id.user_id and
                                       each_emp_id.user_id.id)]
                        })
                        groups_ids.write({'users': [(4, each_emp_id.user_id and
                                                     each_emp_id.user_id.id)]
                                          })
        return res


class DocumentRequest(models.Model):
    _name = 'document.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _desription = 'Employee Document Request'

    _rec_name = 'employee_id'

    name = fields.Char(string='Document Request', copy=False)
    employee_id = fields.Many2one('hr.employee',
                                  string="Employee")
    document_type_id = fields.Many2one('document.type',
                                       string='Document Type')
    req_date = fields.Date(string='Request Date')
    description = fields.Text(string='Description')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('approved', 'Approve'),
                              ('reject', 'Reject'),
                              ('received', 'Received'),
                              ],
                             default='draft',
                             track_visibility='onchange')

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].get('document.request')
        vals.update({'name': name})
        return super(DocumentRequest, self).create(vals)

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.write({'state': 'confirm'})

    @api.multi
    def action_approved(self):
        for rec in self:
            rec.write({'state': 'approved'})

    @api.multi
    def action_received(self):
        for rec in self:
            rec.write({'state': 'received'})

    @api.multi
    def action_reject(self):
        for rec in self:
            rec.write({'state': 'reject'})
