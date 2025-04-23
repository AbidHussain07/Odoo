from odoo import models, api, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    confirmed_user_id = fields.Many2one('res.users' ,string="Confirmed By", readonly=True)

    # inheriting the function from the original class
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.confirmed_user_id = self.env.user.id
        return res
    
    def prepare_invoice(self):
        invoice_vals = super(SaleOrder, self).prepare_invoice()
        invoice_vals['confirmed_user_id'] = self.confirmed_user_id.id
        return invoice_vals
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
