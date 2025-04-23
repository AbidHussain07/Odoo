from odoo import models, fields,api
from datetime import datetime,timedelta

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = 'schedule_date'

    subscription_id = fields.Many2one('sale.order', string='Subscription' )
    meal_type = fields.Selection([('lunch', 'Lunch'), ('dinner', 'Dinner')], string='Meal Type', default='lunch', required=True)
    schedule_date = fields.Date(string='Delivery Date')

    @api.depends('move_ids.state', 'move_ids.date', 'move_type', 'schedule_date')
    def _compute_scheduled_date(self):
        for picking in self:
            if picking.subscription_id.plan_id:
                if picking.schedule_date:
                    picking.scheduled_date = picking.schedule_date
                else:
                    moves_dates = picking.move_ids.filtered(lambda move: move.state not in ('done', 'cancel')).mapped('date')
                    if picking.move_type == 'direct':
                        picking.scheduled_date = min(moves_dates, default=picking.scheduled_date or fields.Datetime.now())
                    else:
                        picking.scheduled_date = max(moves_dates, default=picking.scheduled_date or fields.Datetime.now())


    def button_validate(self):
        super(StockPicking, self).button_validate()
        return True
        
    
    # def action_regenerate(self):
    #     for picking in self:
    #         if picking.state != 'cancel':
    #             picking.action_cancel()
    #         subscription = picking.subscription_id
    #         subscription_deliveries = self.search([
    #             ('subscription_id', '=', subscription.id),
    #             ('state', 'not in', ['cancel']),
    #             ('scheduled_date', '>', picking.scheduled_date),
    #         ], order='scheduled_date asc')

    #         if subscription_deliveries:
    #             last_delivery_date = subscription_deliveries[-1].scheduled_date
    #         else:
    #             last_delivery_date = fields.Date.from_string(subscription.date_order)

    #         new_delivery_date = last_delivery_date + timedelta(days=1)

    #         new_picking = self.create({
    #             'partner_id': subscription.partner_id.id,
    #             'scheduled_date': new_delivery_date,
    #             'schedule_date': new_delivery_date,
    #             'location_id': self.env.ref('stock.stock_location_stock').id,
    #             'location_dest_id': subscription.partner_id.property_stock_customer.id,
    #             'move_type': 'direct',
    #             'picking_type_id': picking.picking_type_id.id,
    #             'origin': subscription.name,
    #             'subscription_id': subscription.id,
    #         })
    #         for move in picking.move_ids:
    #             self.env['stock.move'].create({
    #                 'name': move.name,
    #                 'product_id': move.product_id.id,
    #                 'product_uom_qty': move.product_uom_qty,
    #                 'product_uom': move.product_uom.id,
    #                 'location_id': move.location_id.id,
    #                 'location_dest_id': move.location_dest_id.id,
    #                 'picking_id': new_picking.id,
    #             })
    #         new_picking.action_confirm()



    def action_cancel(self):
        super(StockPicking, self).action_cancel()
        # self.action_regenerate()
        return True
            