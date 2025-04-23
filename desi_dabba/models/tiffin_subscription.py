from odoo import api, fields, models,exceptions
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class TiffinSubscription(models.Model):
    _inherit = 'sale.order'

    delivery_order_ids = fields.One2many('stock.picking',  'subscription_id',  string='Delivery Orders:')
    # is_subscription_confirmed = fields.Boolean(string='Subscription Confirmed',compute="_compute_check_invoice_status", store=True)
    get_invoice_ids = fields.One2many('account.move', 'give_invoice_id', string='Invoice Ids')
    meal_type = fields.Selection([ ('lunch', 'Lunch'),('dinner', 'Dinner')], string='Meal Type', required=True , default='lunch')
    delivery_order_count = fields.Integer( string='Delivery Orders Count', compute='_compute_delivery_order_count' )
    # working_day_ids = fields.Many2many('working.days','sale_id', string='Working Days', default=lambda self: self._default_partners())
    working_day_ids = fields.Many2many(
    'working.days',
    'sale_order_working_days_rel',  # Custom relation table name
    'order_id',  # Column for sale.order
    'working_day_id',  # Column for working.days
    string='Working Days'
)
    
    def _compute_delivery_order_count(self):
        for subscription in self:
            subscription.delivery_order_count = len(subscription.delivery_order_ids)
    
    def _default_partners(self):
        return [(6, 0, self.env['working.days'].search([], limit=6).ids)]

    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     self.partner_shipping_id = self.partner_id

    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     if self.partner_id:
    #         complex_name = self.partner_id.complex_id.name if self.partner_id.complex_id else ''
    #         wing_name = self.partner_id.wing_id.name if self.partner_id.wing_id else ''
    #         office_no = self.partner_id.office_no if self.partner_id.office_no else ''

    #         shipping_address = self.env['res.partner'].create({
    #             'name': complex_name + " " + wing_name + " " + office_no,
    #         })
    #         self.partner_shipping_id = shipping_address


    def _get_working_days(self, start_date, days_count):
        delivery_days = self.working_day_ids.mapped('day_index')
        working_days = []
        current_date = start_date
        holiday_dates = self.env['tiffin.holiday'].search([]).mapped('date')

        while len(working_days) < days_count:
            if (str(current_date.weekday()) in delivery_days and current_date not in holiday_dates): 
                working_days.append(current_date)
            current_date += timedelta(days=1)  # Move to the next day

        return working_days


# ==================================AI GENERATED==========================================================
    # def _get_working_days(self, start_date, days_count):
    #     delivery_days = self.working_day_ids.mapped('day_index')
    #     working_days = []
    #     current_date = start_date
    #     holiday_dates = self.env['tiffin.holiday'].search([]).mapped('date')
        
    #     # Safety check to prevent infinite loops
    #     max_iterations = 1000  # Adjust as needed
    #     iteration_count = 0
        
    #     while len(working_days) < days_count and iteration_count < max_iterations:
    #         if (str(current_date.weekday()) in delivery_days and 
    #             current_date not in holiday_dates):
    #             working_days.append(current_date)
            
    #         current_date += timedelta(days=1)
    #         iteration_count += 1
        
    #     if len(working_days) < days_count:
    #         raise UserError("Could not find enough working days within the search limit.")
        
    #     return working_days
# ============================================================================================
    
    def action_generate_delivery_orders(self):
        for subscription in self:
            invoice_ids = subscription.get_invoice_ids
            pay = self.env['account.payment'].search([ ('invoice_ids', 'in', [invoice_ids[0].id])])

            print('================================================',pay)
            print('================================================',pay.date)
            # payment = (subscription.get_invoice_ids[0].payment_ids
            start_date = fields.Date.from_string(pay.date + timedelta(days=1)) 
            subscription_type = subscription.plan_id.billing_period_unit
            billing_period_value = subscription.plan_id.billing_period_value
            product = subscription.order_line.product_template_id  
            
            if subscription_type == 'month':
                total_days = 20 * billing_period_value
            elif subscription_type == 'week':
                total_days = 5 * billing_period_value
            elif subscription_type == 'year':
                total_days = 1 * billing_period_value
                subscription.end_date = start_date
            else:
                raise UserError("Unsupported subscription type: %s" % subscription_type)
            
            working_days = self._get_working_days(start_date, total_days)

            print(f"Partner: {subscription.partner_id}")
            print(f"Working Days: {working_days}")
            print(f"Start Date: {start_date}")
            print(f"Total Days: {total_days}")
            print(f"product: {product}")
            
            for delivery_date in working_days:
                
                print(f"Delivery Date: {delivery_date}")
                try:
                    picking_type = self.env['stock.picking.type'].search([
                        ('code', '=', 'outgoing'),
                        ('warehouse_id', '=', subscription.warehouse_id.id)
                    ], limit=1)

                    if not picking_type:
                        raise UserError("No outgoing picking type in warehouse.")
                    
                    if subscription.meal_type == 'lunch':
                        delivery_time = datetime.strptime('06:30:00', '%H:%M:%S').time() 
                    elif subscription.meal_type == 'dinner':
                        delivery_time = datetime.strptime('14:30:00', '%H:%M:%S').time()
                    else:
                        delivery_time = datetime.strptime('06:30:00', '%H:%M:%S').time()

                    scheduled_datetime = datetime.combine(delivery_date, delivery_time)
                        
                    print(f"Scheduled Date: {scheduled_datetime}")
                    
                    picking =self.env['stock.picking'].create({
                        'partner_id': subscription.partner_id.id,
                        'scheduled_date': scheduled_datetime,
                        'meal_type': subscription.meal_type,
                        'schedule_date': delivery_date,
                        'location_id': self.env.ref('stock.stock_location_stock').id,
                        'location_dest_id': subscription.partner_id.property_stock_customer.id,
                        'move_type': 'direct',
                        'picking_type_id': picking_type.id,
                        'origin': subscription.name,
                        'subscription_id': subscription.id,
                    })
                    print(f"Scheduled Date after creation: {picking.scheduled_date}")

                    for order_line in subscription.order_line:
                        self.env['stock.move'].create({
                            'name': order_line.product_id.name,
                            'product_id': order_line.product_id.id,
                            'product_uom_qty': order_line.product_uom_qty,
                            'product_uom': order_line.product_uom.id,
                            'location_id': self.env.ref('stock.stock_location_stock').id,
                            'location_dest_id': subscription.partner_id.property_stock_customer.id,
                            'picking_id': picking.id,  # Link to the picking
                        })
                    picking.action_assign()
                    print(f"Picking State: {picking.state}")
                    print('=============================================================')

                except Exception as e:
                    raise UserError(f"Error creating delivery for {delivery_date}: {str(e)}")      

            next_invoice_date = working_days[-1]
            subscription.next_invoice_date = next_invoice_date
            subscription.get_invoice_ids.next_invoice_date = next_invoice_date
    
    def action_view_delivery_orders(self):
        # self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery Orders',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('subscription_id', '=', self.get_invoice_ids.give_invoice_id.id)],
            'target': 'current',
        }
    
    def action_cancel_next_delivery(self):
        for subscription in self:
            current_date = fields.Date.today() #+ timedelta(days=1)
            picking = None

            while not picking:
                picking = self.env['stock.picking'].search([
                    ('subscription_id', '=', subscription.id),
                    ('schedule_date', '=', current_date),
                    ('state', 'not in', ['done', 'cancel'])
                ], limit=1)

                if not picking:
                    current_date += timedelta(days=1)  # Move to the next day
                    if current_date > subscription.next_invoice_date:  
                        raise UserError("No more scheduled deliveries to cancel.")  

            picking.action_cancel()

            last_delivery_date = subscription.next_invoice_date
            next_working_day = subscription._get_working_days(last_delivery_date + timedelta(days=1), 1)[0]

            new_picking = picking.copy({
                'schedule_date': next_working_day,
                'scheduled_date': datetime.combine(next_working_day, picking.scheduled_date.time())
            })

            new_picking.action_assign()
            subscription.next_invoice_date = next_working_day

            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Next available Delivery Cancelled\n & \nNew Delivery Scheduled!',
                    'type': 'rainbow_man'
                }
            }
        
    # def action_confirm(self):
    #         for order in self:
    #             if order.state != 'draft':
    #                 raise exceptions.UserError("Some orders are not in a state requiring confirmation.")
    #         return self._action_confirm()

    # def action_confirm(self):
    #     for order in self:
    #         if order.state != 'draft':
    #             raise exceptions.UserError("Some orders are not in a state requiring confirmation.")
    #         if order.plan_id:
    #             return self._custom_action_confirm()
    #         else:
    #             return super().action_confirm()

    # def _action_confirm(self):
    #     res = super()._action_confirm()
    #     for order in self:
    #         pickings = order.picking_ids.filtered(lambda p: p.state in ['draft', 'assigned'])
    #         pickings.action_cancel()
    #     return res

    def _action_confirm(self):
        res = super()._action_confirm()
        for order in self:
            meal_text = order.meal_type.capitalize() if order.meal_type else ''
            working_days = ', '.join(order.working_day_ids.mapped('name')) if order.working_day_ids else ''

            order.website_order_line.name = f'Meal Type {meal_text} \n Days:- {working_days}' if working_days else meal_text

            pickings = order.picking_ids.filtered(lambda p: p.state in ['draft', 'assigned'])
            pickings.action_cancel()

        return res

class WorkingDays(models.Model):
    _name = 'working.days'
    _description = 'Working Days'

    sale_id = fields.Many2one('sale.order', string='Sale Order')
    name = fields.Char(string='Days', required=True, )
    day_index = fields.Char(string='Day Index', required=True)

class SaleSubscriptionPlanExt(models.Model):
    _inherit = 'sale.subscription.plan'

    billing_period_unit = fields.Selection(selection_add=[('day', 'Day')], ondelete={'day': 'cascade'})