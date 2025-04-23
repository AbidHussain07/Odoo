from odoo import models, api, fields, _
import datetime
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from datetime import date

class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = "Cancelling the Appointment"

    @api.model
    def default_get(self, fields):
        res = super(CancelAppointmentWizard, self).default_get(fields)
        res['appointment_id'] = self.env.context.get('active_id')
        res['cancel_date'] = datetime.date.today()
        return res
    
    appointment_id = fields.Many2one('hospital.appointment' ,string="Appointment")
    reason = fields.Text(string="Reason")
    cancel_date = fields.Date(string="Cancellation Date")

    def action_cancel(self):
        cancel_day = self.env['ir.config_parameter'].sudo().get_param('hospital.cancel_days')
        allow_date = self.appointment_id.date - relativedelta.relativedelta(days=int(cancel_day))
        if allow_date < date.today():
            raise ValidationError(_(f"You can't cancel the appointment.\nCancellation can be done {cancel_day} days before the appointment date."))
        else:
            self.appointment_id.state = 'cancel'
            return {
                "type" : "ir.actions.client",
                "tag" : "reload"
            }


# For Simple Cancelation without getting any data from settings
        # if self.appointment_id.date < self.cancel_date:
        #     raise ValidationError(_("The Appointment date is already passed."))
        # elif self.appointment_id.date == self.cancel_date:
        #     raise ValidationError(_("Sorry! You can't cancel the appointment on the same day."))
        # else:
        #     self.appointment_id.state = 'cancel'
        # return
