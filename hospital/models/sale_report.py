from odoo import models, api, fields

class SaleReport(models.Model):
    _inherit = 'sale.report'

    confirmed_user_id = fields.Many2one('res.users' ,string="Confirmed By", readonly=True)
    
    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['confirmed_user_id'] = "s.confirmed_user_id"
        return res