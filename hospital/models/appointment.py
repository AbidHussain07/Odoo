from odoo import models, api, fields,_
from odoo.exceptions import ValidationError
from datetime import datetime

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Patient Appointment"
    _rec_names_search = ["patient_id","reference"]
    _rec_name = "patient_id"
    _order = "id desc"

    reference = fields.Char(string="Reference Id" ,default="HOS####")
    patient_id = fields.Many2one("hospital.patient", string="Patient Name", required=True, tracking=True)
    # date = fields.Date(string="Appointment Date", tracking=True)
    appointment_time = fields.Datetime(string="Appointment Time", tracking=True, default=fields.Datetime.now)
    specialization_id = fields.Many2one('hospital.specialist', string='Speciality',required=True)
    doctor_id = fields.Many2one("hospital.doctor", string="Doctor", required=True, tracking=True, domain="[('specialization', '=', specialization_id)]")
    
    @api.onchange('specialization_id')
    def _onchange_specialty_id(self):
        """Reset doctor field if specialty is changed after selecting a doctor."""
        if self.doctor_id and self.doctor_id.specialization != self.specialization_id:
            self.doctor_id = False

    # doctor_id = fields.Many2one("hospital.doctor", string="Doctor", required=True, tracking=True)
    total_qty = fields.Float(compute="_compute_total_qty" ,string="Total Fees:" ,help="Total Fees of the Appointment")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('ongoing','Ongoing'),('done','Done'),('cancel','Cancelled')],default='draft',tracking=True)
    appointment_ids = fields.One2many('hospital.appointment.line', 'appointment_id', string='Appointment Lines')
    dob = fields.Date(string="Date of Birth", related='patient_id.dob')
    prescription = fields.Html(string="Prescription")
    # hide_disease = fields.Boolean(string="Hide Disease")
    progress = fields.Integer(string="Progress", compute="_compute_progress")
    duration = fields.Float(string="Duration")
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency' ,related='company.currency_id')

    def unlink(self):
        if self.state != 'draft':
                raise ValidationError(_("You cannot delete the Patient Appointment.\nOnly Draft-status can be deleted."))
        return super().unlink()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals['reference']=="HOS####":
                vals['reference']= self.env['ir.sequence'].next_by_code('hospital.appointment')
        return super().create(vals_list)
    
    def write(self, vals):
        return super(HospitalAppointment, self).write(vals)

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.reference} - {rec.patient_id.name}"
        # return (rec.id,'%s: %s' % (rec.reference, rec.patient_id.name) for rec in self) #instead of above 2 lines.

    def _compute_total_qty(self):
        for rec in self:
            total_qty = 0
            for line in rec.appointment_ids:
                total_qty +=line.price
            rec.total_qty = total_qty

            # short method to note dowm
            # rec.total_qty = sum(rec.appointment_ids.mapped('qty'))

    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft':
                rec.progress = 25
            elif rec.state == 'confirm':
                rec.progress = 50
            elif rec.state == 'ongoing':
                rec.progress = 75
            elif rec.state == 'done':
                rec.progress = 100
            else:
                rec.progress = 0
    
    def action_confirm(self):
        for i in self:
            i.state = 'confirm'

    def action_ongoing(self):
        for i in self:
            i.state = 'ongoing'

    def action_done(self):
        for i in self:
            i.state = 'done'
        return {
                'effect': {
                    'fadeout': 'slow',
                    'message': "The appointment is done",
                    'type': 'rainbow_man',
                }
            }
            
    def action_cancel(self):
        action = self.env.ref('hospital.action_cancel_appointment').read()[0] #read()[0] mandatory to call and read action
        return action
    
    def action_draft(self):
        for i in self:
            i.state = 'draft'

    def action_test(self):
        # url action 
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://abidhussain07.github.io',
            'target': 'new',
        }
    
    def action_whatsapp(self):
        if not self.patient_id.mobile:
            raise ValidationError('There is no Mobile number in this record.\nPlease add Mobile number of the Patient')
        dt = self.appointment_time.time()
        dd = self.appointment_time.date()
        message = 'Hello,*%s* your appointment is scheduled on *%s* at *%s* with Dr.*%s*.\n Thank you!' % (self.patient_id.name, dd,dt, self.doctor_id.name)
        whatsapp_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.patient_id.mobile, message)
        # for showing it in chatter same as tracking
        self.message_post(body="Whatsapp message sent to %s" % self.patient_id.mobile ,subject="Whatsapp Message")

        # url action 
        return {
            'type': 'ir.actions.act_url',
            'url': whatsapp_url,
            'target': 'new',
        }
    
    # # Notification
    def action_notification(self):
        title = 'Appointment Confirmed'
        message = 'The Appointment is confirmed for %s' % self.patient_id.name
        next_action = {
            # 'name': _('View Patient'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.patient',
            'res_id': self.patient_id.id,
            # 'False' ensures Odoo picks the default form view.===>[=== 'views': [(self.env.ref('module_name.view_patient_form').id, 'form')] ===]
            'views': [(False, 'form')],
        }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'type': 'success',
                'message': message,
                'next': next_action,
            }
        }
        # return {
        #         'type': 'ir.actions.client',
        #         'tag': 'display_notification',
        #         'params': {
        #                 'title': _('Appointment Confirmed'),
        #                 'message': '%s',
        #                 'links': [{
        #                     'label': self.patient_id.name,
        #                     'url': f'/odoo/action-177/{self.patient_id.id}?debug=1/'
        #                 }],
        #                 'sticky': False,
        #                 'next': {
        #                     'type': 'ir.actions.act_window',
        #                     'res_model': 'hospital.patient',
        #                     'res_id': self.patient_id.id,
        #                     'views': [(False, 'form')],
        #                 }
        #         }
        #     }

    # understanding of ORM methods
    # def test_recordset(self):
    #     for rec in self:
    #         patient = self.env['hospital.patient'].search([])
    #         print(patient.mapped('name'))
    #         print(patient.sorted(lambda r: r.name))
    #         # print(patient.filtered(lambda r: r.minor))
    #         print(patient.filtered(lambda r: r.minor == False))

    # ============= For Date Validation =============
    # @api.constrains('date')
    # def _check_date(self):
    #     if self.date < fields.Date.today():
    #         raise ValidationError('The Appointment date should not be of past !')

    # ============= For Time & Date Validation =============
    # @api.constrains('appointment_time', 'date')
    # def _check_appointment_time(self):
    #     for record in self:
    #         if record.appointment_time and record.date:
    #             # Compare the date part of appointment_time with the booking date
    #             appointment_date = record.appointment_time.date()
    #             if appointment_date != record.date:
    #                 raise ValidationError("The Appointment time should be on the same Booking Date!")
                
    #             # Check if the time is in the past
    #             current_time = datetime.now()
    #             if record.appointment_time < current_time:
    #                 raise ValidationError("The Appointment time cannot be in the past!")

    # ============= For Time Validation =============
    @api.constrains('appointment_time')
    def _check_appointment_time(self):
        for record in self:
            if record.appointment_time:
                appointment_date = record.appointment_time.date()
                current_date = fields.Date.today()
                if appointment_date <= current_date:
                    raise ValidationError("The Appointment time should be scheduled for a future date, not today or in the past!")
                
    def action_send_email(self):
        template = self.env.ref('hospital.mail_template_appointment_id')
        if template:
            template.send_mail(self.id, force_send=True)
        else:
            raise ValidationError(_('Email template not found.'))

        
    # As the editable related field can change the value of the parent record it is always a good practice to use onchange 
    # instead of a related attribute, to avoid modifying the model from which we derive the current value.
    # @api.onchange('patient_id')
    # def _onchange_patient_id(self):
    #     if self.patient_id:
    #         self.dob = self.patient_id.dob


class HospitalAppointmentLine(models.Model):
    _name = 'hospital.appointment.line'
    _description = "Patient Appointment Line"

    appointment_id = fields.Many2one('hospital.appointment',string="Appointment Id")
    disease_id = fields.Many2one('patient.tag', string='Disease',required=True)
    price = fields.Float(string="Fees")
    qty = fields.Float(string="Quantity", default=1)
    currency_id = fields.Many2one(related='appointment_id.currency_id', readonly=True)
    sub_total = fields.Monetary(string="Sub Total", compute="_compute_sub_total", store=True)

    @api.depends('price', 'qty')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.price * rec.qty
