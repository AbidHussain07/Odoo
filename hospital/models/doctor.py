from odoo import models, api, fields

class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _inherit = ['mail.thread']
    _description = "Hospital Doctor's"

    name = fields.Char(string="Name", required=True, tracking=True)
    user_id = fields.Many2one('res.users', string="Related User",tracking=True,
                              domain=lambda self: [('groups_id', 'in', self.env.ref('hospital.group_hospital_doctor').ids),
                                                   ('id', 'not in', self._get_doctor_users_ids())])
                    # domain="[('groups_id', 'in', [(4, ref('hospital.group_hospital_doctor_own_id'))])]"
    def _get_doctor_users_ids(self):
    # Fetch all doctors and get their associated user IDs
        return self.env['hospital.doctor'].search([]).mapped('user_id.id')

    profile = fields.Binary(string="Profile Picture", compute='_compute_profile', store=False, readonly=True)
    # Compute the profile image from the related user's profile image
    def _compute_profile(self):
        for doctor in self:
            if doctor.user_id:
                doctor.profile = doctor.user_id.image_1920  # Get the profile image from the related user

    def get_image_base64(self):
        if self.profile:
            return "data:image/jpeg;base64," + self.profile.decode("utf-8")
        return False
    
    gender = fields.Selection([('male','Male'),('female','Female'),('other','Other')],string="Gender",tracking=True)
    location = fields.Char(string="Location", required=True, tracking=True)
    specialization = fields.Many2one('hospital.specialist',string="Specialization",required=True)
    # tag_ids = fields.Many2many('patient.tag','tag_db','patient_id','tag_id' ,string="Tags")

class Specialist(models.Model):
    _name = 'hospital.specialist'
    _description = "Specialize"
    _order = "sequence,id"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default='1')

# class DoctorSpecialist(models.Model):
#     _name = 'hospital.doctor.specialist'
#     _description = "Specialist Doctor"

#     doctor_id = fields.Many2one('hospital.doctor',string="Appointment Id",required=True)
#     specialist_id = fields.Many2one('hospital.specialist', string='Specialist',required=True)