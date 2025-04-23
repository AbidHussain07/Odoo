from odoo import models,fields,api
from datetime import datetime

class AppointmentExampleWizard(models.TransientModel):
    _name = 'example.appointment.wizard'
    _description = "Print the Appointment"

    patient_id = fields.Many2one("hospital.patient", string="Patient Name", required=True)
    date_from = fields.Date(string="Date From :")
    date = fields.Date(string="Till Date :")


    def action_print(self):
        domain = []
        patient_id = self.patient_id
        if patient_id:
            domain += [('patient_id', '=', patient_id.id)]
        
        # Handle the date_from field, converting it to datetime
        date_from = self.date_from
        if date_from:
            # Convert date_from to datetime, with time set to 00:00:00 (start of the day)
            date_from_datetime = datetime.combine(date_from, datetime.min.time())
            domain += [('appointment_time', '>=', date_from_datetime)]
        
        # Handle the date_to field, converting it to datetime
        date_to = self.date
        if date_to:
            # Convert date_to to datetime, with time set to 23:59:59 (end of the day)
            date_to_datetime = datetime.combine(date_to, datetime.max.time())
            domain += [('appointment_time', '<=', date_to_datetime)]
        
        # Search for appointments based on the domain
        appointments = self.env['hospital.appointment'].search_read(domain)

        # Prepare the data to pass to the report
        data = {
            'form': self.read()[0],  # Passing the form data properly
            'appointments': appointments
        }
        
        return self.env.ref('hospital.action_report_example_appointment').report_action(self, data=data)


class DoctorDetailReport(models.AbstractModel):
    _name = 'report.hospital.report_doctor_card'
    _description = "Doctor Detail Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hospital.doctor'].browse(docids)
        
        # Data you need to pass to the template
        return {
            'docs': docs,
        }