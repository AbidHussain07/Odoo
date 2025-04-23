from odoo import http
from odoo.http import request
from werkzeug.utils import redirect
import json
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleCustom(WebsiteSale):
    
    # This will override the default cart_update function
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def custom_cart_update(self, product_id, add_qty=1, set_qty=0, product_custom_attribute_values=None,
                           no_variant_attribute_value_ids=None, meal_type=None, working_days=None, plan_id=None, **kwargs):
        
        # Debugging: Check if the controller method is being triggered
        _logger.info("custom_cart_update method triggered")

        # Get the current order (or create one if it doesn't exist)
        order = request.website.sale_get_order(force_create=1)
        if not order:
            return request.redirect('/shop')

        # Process the working days (splitting by commas and converting to integer)
        working_days_ids = [int(day) for day in working_days.split(",") if day.isdigit()] if working_days else []
        
        # Debugging: Check the processed working_days
        _logger.info(f"Working Days: {working_days_ids}")

        # Update the sale order with the additional fields (meal_type, working_days, plan_id)
        order.sudo().write({
            'meal_type': meal_type,
            'working_day_ids': [(6, 0, working_days_ids)],
            'plan_id': int(plan_id) if plan_id else False
        })

        # Debugging: Log the updated order values
        _logger.info(f"Order updated: Meal Type: {meal_type}, Plan ID: {plan_id}, Working Days: {working_days_ids}")

        # Call the original cart update function with all the parameters
        return super(WebsiteSaleCustom, self).cart_update(
            product_id=product_id, 
            add_qty=add_qty, 
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_value_ids=no_variant_attribute_value_ids,
            **kwargs
        )



# class WebsiteSaleCustom(http.Controller):

#     @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
#     def custom_cart_update(self, product_id, add_qty=1, meal_type=None, working_days=None, plan_id=None, **kwargs):
#         order = request.website.sale_get_order(force_create=1)

#         if not order:
#             return request.redirect('/shop')

#         working_days_ids = [int(day) for day in working_days.split(",") if day.isdigit()] if working_days else []

#         order.sudo().write({
#             'meal_type': meal_type,
#             'working_day_ids': [(6, 0, working_days_ids)],
#             'plan_id': int(plan_id) if plan_id else False  
#         })

#         # Update cart
#         order._cart_update(
#             product_id=int(product_id),
#             add_qty=int(add_qty),
#             set_qty=0,
#             linked_line_id=None
#         )

#         return request.redirect('/shop/cart')
