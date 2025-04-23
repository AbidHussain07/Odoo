from odoo import models, api, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    appointment_id = fields.Many2one('hospital.appointment' , string="Appointment")

    # inheriting the function from the original class
    def action_post(self):
        res = super(AccountMove, self).action_post()
        # if self.appointment_id:
        #     self.appointment_id.state = 'done'
        # return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lines = fields.Integer(string="Lines")