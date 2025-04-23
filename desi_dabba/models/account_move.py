from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    give_invoice_id = fields.Many2one('sale.order', string="Sale-Order Id")
    is_invoice_confirmed = fields.Boolean(string='Invoice Confirmed', default=False)
    next_invoice_date = fields.Date(string="Next Invoice Date") 
    delivery_trigger_field = fields.Char(string="Delivery Trigger", compute="_compute_delivery_trigger", store=True)
    delivery_triggered = fields.Boolean(string="Delivery Triggered", default=False, copy=False)

    @api.depends('status_in_payment')
    def _compute_delivery_trigger(self):
        for record in self:
            if record.give_invoice_id.plan_id:
                if record.status_in_payment == 'draft':
                    record.delivery_trigger_field = "Order in Draft Stage"
                elif record.status_in_payment == 'in_payment':
                    record.delivery_trigger_field = "Payment in Progress"
                elif record.status_in_payment == 'paid':
                    record.delivery_trigger_field = "Ready for Delivery 🚀"

                    if not record.delivery_triggered and record.give_invoice_id:
                        print("********** Generating Delivery Order **********")
                        record.give_invoice_id.action_generate_delivery_orders()
                        record.delivery_triggered = True  
                elif record.status_in_payment == 'cancel':
                    record.delivery_trigger_field = "Order Cancelled"

    @api.onchange('next_invoice_date')
    def _onchange_next_invoice_date(self):
        for record in self:
            if record.give_invoice_id.plan_id:
                record.delivery_triggered = False 
        
    @api.model
    def create(self, vals):
        if 'invoice_origin' in vals:
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order:
                vals['give_invoice_id'] = sale_order.id
        return super(AccountMove, self).create(vals)
  
