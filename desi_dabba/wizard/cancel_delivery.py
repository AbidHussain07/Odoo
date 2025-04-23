# from odoo import models, fields, api
# from datetime import timedelta,datetime
# from odoo.exceptions import UserError

# class RescheduleDeliveryWizard(models.TransientModel):
#     _name = 'reschedule.delivery.wizard'
#     _description = 'Reschedule Delivery Wizard'

#     cancel_date = fields.Date(string='Date to Cancel Deliveries', required=True, default=fields.Date.today)

#     def _get_working_days_from_sale_order(self, start_date, days_count):
#         sale_order_model = self.env['sale.order']
#         return sale_order_model._get_working_days(start_date, days_count)

# # =================================AI GENERATED===========================================================
#     # def _get_working_days_from_sale_order(self, start_date, days_count):
#     #     if not start_date:
#     #         raise UserError("Start date is required.")
            
#     #     sale_order_model = self.env['sale.order']
#     #     return sale_order_model._get_working_days(start_date, days_count)
# # ============================================================================================
    
#     # def action_cancel_and_reschedule_deliveries(self):
#     #     if not self.cancel_date:
#     #         raise UserError("Please select a date to cancel deliveries.")
#     #     cancel_date = cancel_date
#     #     pickings_to_cancel = self.env['stock.picking'].search([
#     #         ('scheduled_date', '=', cancel_date),
#     #         ('state', 'not in', ('done', 'cancel'))
#     #     ])

#     #     for picking in pickings_to_cancel:
#     #         picking.action_cancel()

#     #         subscription = picking.subscription_id
#     #         if not subscription:
#     #             continue

#     #         last_scheduled_picking = self.env['stock.picking'].search([
#     #             ('subscription_id', '=', subscription.id),
#     #             ('state', '!=', 'cancel')
#     #         ], order="scheduled_date desc", limit=1)

#     #         last_delivery_date = last_scheduled_picking.scheduled_date if last_scheduled_picking else cancel_date
#     #         print('================================',last_delivery_date)
#     #         print('================================',cancel_date)

#     #         next_delivery_date = last_delivery_date + timedelta(days=1)
#     #         print("=========================================",next_delivery_date)
#     #         next_working_days = self._get_working_days_from_sale_order(next_delivery_date, 1)
#     #         next_delivery_date = next_working_days[0]
#     #         print(f"Next Delivery Date: {next_delivery_date}")

#     #         new_picking = picking.copy({
#     #             'scheduled_date': next_delivery_date,
#     #             'schedule_date': next_delivery_date,
#     #         })
#     #         print(f"New Picking: {new_picking}")
#     #         print(f"New Picking Scheduled Date: {new_picking.scheduled_date}")
#     #         print(f"New Picking Schedule Date: {new_picking.schedule_date}")
#     #         new_picking.action_assign()

#     #         last_delivery_date = next_delivery_date
#     #     return {
#     #     'type': 'ir.actions.client',
#     #     'tag': 'reload',
#     # }
# # =================================================================================================================
#     def action_cancel_and_reschedule_deliveries(self):
#         """Cancel all deliveries on the selected date and reschedule them"""
        
#         if not self.cancel_date:
#             raise UserError("Please select a date to cancel deliveries.")

#         cancel_date = self.cancel_date

#         pickings_to_cancel = self.env['stock.picking'].search([
#             ('schedule_date', '=', cancel_date),
#             ('state', 'not in', ('done', 'cancel'))
#         ])

#         print(f'Cancel Delivery Date{cancel_date}')
#         print(f'Picking to Cancel{pickings_to_cancel}')

#         if not pickings_to_cancel:
#             raise UserError("No deliveries scheduled on this date.")

#         subscriptions_to_update = pickings_to_cancel.mapped('subscription_id')

#         print(f'subscriptions_to_update {subscriptions_to_update}')


#         for subscription in subscriptions_to_update:
#             subscription_pickings = pickings_to_cancel.filtered(lambda p: p.subscription_id == subscription)
#             subscription_pickings.action_cancel()

#             last_delivery = self.env['stock.picking'].search([
#                 ('subscription_id', '=', subscription.id),
#                 ('state', '!=', 'cancel')
#             ], order="schedule_date desc", limit=1)

#             print(f'Last Delivery{last_delivery}')

#             last_delivery_date = last_delivery.schedule_date if last_delivery else cancel_date
#             print(f'Last Delivery Date{last_delivery_date}')


#             next_working_day = self._get_working_days_from_sale_order(last_delivery_date + timedelta(days=1), 1)
#             if not next_working_day:
#                 raise UserError(f"No working days available for subscription {subscription.name}.")

#             next_delivery_date = next_working_day[0]

#             for picking in subscription_pickings:
#                 new_picking = picking.copy({
#                     'schedule_date': next_delivery_date,
#                     'scheduled_date': next_delivery_date,
#                 })
#                 new_picking.action_assign()

#             subscription.next_invoice_date = next_delivery_date

#         return {
#             'effect': {
#                 'fadeout': 'slow',
#                 'message': f"All deliveries on {cancel_date} canceled and rescheduled!",
#                 'type': 'rainbow_man'
#             }
#         }
# # ==========================================================================================

from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError

class RescheduleDeliveryWizard(models.TransientModel):
    _name = 'reschedule.delivery.wizard'
    _description = 'Reschedule Delivery Wizard'

    date = fields.Date(string='Date to Cancel Deliveries', required=True, default=fields.Date.today)
    working_day_ids = fields.Many2many('working.days', string="Working Days")  # Store selected working days

    @api.model
    def default_get(self, fields_list):
        """ Fetch working days from Sale Order and set them in the wizard """
        res = super(RescheduleDeliveryWizard, self).default_get(fields_list)
        active_sale_orders = self.env['sale.order'].search([('state', '=', 'sale')])  # Active subscriptions
        
        if active_sale_orders:
            all_working_days = active_sale_orders.mapped('working_day_ids')
            res['working_day_ids'] = [(6, 0, all_working_days.ids)]  # Set working days in wizard

        return res

    def _get_working_days(self, start_date, days_count):
        """ Fetch working days from wizard instead of Sale Order """
        delivery_days = list(map(int, self.working_day_ids.mapped('day_index')))  # Convert to integer list

        if not delivery_days:
            raise UserError("No working days selected in the wizard.")

        working_days = []
        current_date = start_date
        holiday_dates = self.env['tiffin.holiday'].search([]).mapped('date')

        while len(working_days) < days_count:
            if (current_date.weekday() in delivery_days and current_date not in holiday_dates):
                working_days.append(current_date)
            current_date += timedelta(days=1)

        return working_days

    def action_cancel_and_reschedule_deliveries(self):
        """ Cancel deliveries and reschedule on the next working day """
        if not self.date:
            raise UserError("Please select a date to cancel deliveries.")

        cancel_date = self.date

        # Find deliveries scheduled for this date
        pickings_to_cancel = self.env['stock.picking'].search([
            ('scheduled_date', '=', cancel_date),
            ('state', 'not in', ('done', 'cancel'))
        ])

        if not pickings_to_cancel:
            raise UserError("No deliveries found for this date.")

        subscriptions_to_update = pickings_to_cancel.mapped('subscription_id')
        print(f"subscription to update{subscriptions_to_update}")
        for picking in pickings_to_cancel:
            picking.action_cancel() 

        for subscription in subscriptions_to_update:
            if not subscription:
                continue

            last_scheduled_picking = self.env['stock.picking'].search([
                ('subscription_id', '=', subscription.id),
                ('state', '!=', 'cancel')
            ], order="scheduled_date desc", limit=1)

            print("Last Scheduled Picking",last_scheduled_picking)

            last_delivery_date = last_scheduled_picking.scheduled_date if last_scheduled_picking else cancel_date
            print(f"last delivery date",last_delivery_date)
            next_working_days = self._get_working_days(last_delivery_date + timedelta(days=1), 1)
            print("next working days",next_working_days)
            if not next_working_days:
                raise UserError(f"No available working day found after {last_delivery_date}.")

            next_delivery_date = next_working_days[0]
            print("Next delivery Date",next_delivery_date)

            new_picking = picking.copy({
                'scheduled_date': next_delivery_date,
                'schedule_date': next_delivery_date,
            })
            print(f'New picking ------ {new_picking}')

            new_picking.action_assign()  

        return {'type': 'ir.actions.client', 'tag': 'reload'}
