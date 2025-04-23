from odoo import models, api, fields,_
#  '_' is used to translate the text inside the string if possible
from odoo.exceptions import ValidationError , UserError
from datetime import date
from dateutil import relativedelta

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Patient Master"

    name = fields.Char(string="Name", required=True, tracking=True)
    patient_image = fields.Binary(string="Patient Image")
    def get_image_base64(self):
        if self.patient_image:
            return "data:image/jpeg;base64," + self.patient_image.decode("utf-8")
        return False

    dob = fields.Date(string="Date of Birth", tracking=True)
    age = fields.Integer(compute="_compute_age",search="_search_age", string="Age")
    gender = fields.Selection([('male','Male'),('female','Female'),('other','Other')],string="Gender",tracking=True)
    tag_ids = fields.Many2many('patient.tag','tag_db','patient_id','tag_id' ,string="Disease")
    minor = fields.Boolean(string="Minor", tracking=True)
    guardian_relation = fields.Selection([('husband','Husband'),('father','Father'),('mother','Mother'),('sister','Sister'),('brother','Brother'),('other','Other')],string="Guardian Relation")
    guardian_name = fields.Char(string="Guardian Name")
    active = fields.Boolean(string="Active", default=True)
    priority = fields.Selection([('very-low','Very Low'),('low','Low'),('normal','Normal'),('medium','Medium'),('high','High'),('very-high','Very High')],string="Priority",default='low',group_expand='_read_full_group')
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string="Appointments")
    appointment_count = fields.Integer(string="Appointment Count", compute="_compute_appointment_count" ,store=True)
    reference_record = fields.Reference([('hospital.doctor','Doctor'),('hospital.patient','Patient')],string="Reference")
    is_birthday = fields.Boolean(string="Is Birthday Today", compute="_compute_is_birthday")
    mobile = fields.Char(string="Mobile Number")
    phone = fields.Char(string="Phone Number")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")

    def unlink(self):
        for rec in self:
            domain = [('patient_id','=' ,rec.id)]
            appointments = self.env['hospital.appointment'].search(domain)
            if appointments:
                raise ValidationError(f"You cannot delete the Patient name {rec.name}.\nBecause it exist in Appointment.")
        return super().unlink()
    
    # # same as above but api method

    # @api.ondelete(at_uninstall=False)
    # def _create_error(self):
    #     for rec in self:
    #         domain = [('patient_id','=' ,rec.id)]
    #         appointments = self.env['hospital.appointment'].search(domain)
    #         if appointments:
    #             raise ValidationError(f"You cannot delete the Patient name {rec.name}.\nBecause it exist in Appointment")
    
    @api.constrains('dob')
    def _check_date(self):
        if self.dob >= fields.Date.today():
            raise ValidationError('The Date of Birth cannot be in Future!')

    @api.depends('dob') # this is a decorator used to change the age when dob is changed or updated instanly    
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.dob:
                rec.age = today.year - rec.dob.year - ((today.month, today.day) < (rec.dob.month, rec.dob.day))
            else:
                rec.age = 0
# =====================================================================
# NOT WORKING PROPERLY THAT WHY COMMENTED
    # @api.depends('age') # this is a decorator used to change the dob when age is changed or updated instanly
    # def _inverse_compute_age(self):
    #     today = date.today()
    #     for rec in self:
    #         month = rec.dob.month if rec.dob else today.month
    #         day = rec.dob.day if rec.dob else today.day
    #         rec.dob = date(today.year, month, day) - relativedelta.relativedelta(years=rec.age)

    # def _search_age(self, operator, value):
    #     """
    #     Custom search method for the `age` field.
    #     :param operator: The comparison operator ('=', '>=', etc.)
    #     :param value: The value to compare (e.g., 25)
    #     :return: A domain for searching records based on `dob`
    #     """
    #     today = date.today()
    #     if operator in ('=', '!=', '<', '<=', '>', '>='):
    #         # Calculate the date range based on the age
    #         start_date = today - relativedelta.relativedelta(years=value + 1)
    #         end_date = today - relativedelta.relativedelta(years=value)
    #         # Return a domain to filter based on `dob`
    #         return [('dob', '>=', start_date), ('dob', '<=', end_date)]
    #     return []
#   =====================================================================      

    def action_cancel(self):
        pass

    @api.depends('dob')
    def _compute_is_birthday(self):
        for rec in self:
            if rec.dob:
                if rec.dob.month == date.today().month and rec.dob.day == date.today().day:
                    rec.is_birthday = True
                else:
                    rec.is_birthday = False
            else:
                rec.is_birthday = False

    def action_appointment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointments',
            'res_model': 'hospital.appointment',
            'view_mode': 'list,form,activity,calendar',
            'domain': [('patient_id','=',self.id)],
            'context': {'default_patient_id': self.id}
        }
    
    def action_sql_query(self):
        query = "select patient_id,appointment_time from hospital_appointment where patient_id = %s" % self.id
        # cr is a cursor object which is used to execute the query
        self.env.cr.execute(query)
        # self._cr.execute(query)

        # to fetch the result in the form of list of tuples
        # result = self.env.cr.fetchall()
        # to fetch the result in the form of dictionary
        result = self.env.cr.dictfetchall()
        # to fetch only opening record
        # result = self.env.cr.fetchone()
        print("================================>",self.id)
        print("================================>",result)
        title = 'Query Executed'
        message = 'Check the console for the result'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'type': 'success',
                'message': message,
            }
        }
# ==============================================================================================================
    # @api.depends('appointment_ids')
    # def _compute_appointment_count(self):
    #     for rec in self:
    #         rec.appointment_count = len(rec.appointment_ids)

    # ORM METHODS ----> search_count
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['hospital.appointment'].search_count([('patient_id','=',rec.id)])

    # ORM METHODS ----> read_group
    # @api.depends('appointment_ids')
    # def _compute_appointment_count(self):
    #     appointment_data = self.env['hospital.appointment'].read_group([('state','=','confirm')],['patient_id'], ['patient_id'])
    #     for data in appointment_data:
    #         patient = self.browse(data['patient_id'][0])
    #         patient.appointment_count = data['patient_id_count']
    #         self -= patient
    #     self.appointment_count = 0
# ==============================================================================================================
    @api.model
    def receive_msg(self):
        title = 'Testing Completed'
        message = 'Cron jobs is working.'
        print('Cron jobs is working.')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'type': 'info',
                'message': message,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
        
    # understanding of special command
    def special_command(self):
        order = self.env['sale.order'].browse(21)

        #create a new order
        # order.write({
        #     'order_line': [(0, 0, {
        #         'product_id': 5,
        #         'product_uom_qty': 2,
        #         'price_unit': 100,
        #     })]
        # })

        # upddate the order
        # order.write({
        #     'order_line': [(1, 46, {
        #         'product_uom_qty': 5
        #     })]
        # })

        # delete the order 
        # order.write({
        #     'order_line': [(2, 46)]
        # })

        # link existing order line 
        # order.write({
        #     'order_line': [(4, 45, 0)]
        # })

        # unlink all orderline from order but don't delete them
        # order.write({
        #     'order_line': [(5, 0, 0)]
        # })

        #  Replace All Lines with New Ones
        order.write({
            'order_line': [(6, 0, [20, 21])]
        })

    @api.model
    def _read_full_group(self,group,domain):
        # This method is used to expand the group in the kanban view
        return [key for key, _ in self._fields['priority'].selection]
