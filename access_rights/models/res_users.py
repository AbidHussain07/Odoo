from odoo import fields, models,api

class ResUsers(models.Model):
    _inherit = 'res.users'

    contact_tag_ids = fields.Many2many(
        comodel_name='res.partner.category',
        string='Contact Tags',
        help='Select tags to restrict access to customers with these tags.'
    )
