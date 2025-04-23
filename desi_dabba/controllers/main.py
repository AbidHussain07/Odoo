from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


# class WebsiteSaleExtended(WebsiteSale):

#     def _get_mandatory_billing_fields(self):
#         fields = super()._get_mandatory_billing_fields()
#         fields.extend(['complex_id', 'wing_id', 'office_no','region_id'])
#         return fields

#     def _get_mandatory_shipping_fields(self):
#         fields = super()._get_mandatory_shipping_fields()
#         fields.extend(['complex_id', 'wing_id', 'office_no','region_id'])
#         return fields

    # @http.route(['/shop/address'], type='http', auth="public", website=True)
    # def shop_address(self, **kw):
    #     response = super().shop_address(**kw)
    #     _logger.info("Form Data Received: %s", kw)  # Log the received data

    #     if kw.get('partner_id'):
    #         partner = request.env['res.partner'].browse(int(kw['partner_id']))
    #         _logger.info("Updating Partner: %s", partner.name)

    #         # Ensure the fields are being passed correctly
    #         complex_id = int(kw.get('complex_id', 0)) or False
    #         wing_id = int(kw.get('wing_id', 0)) or False
    #         office_no = kw.get('office_no', '')

    #         _logger.info("Writing Data: complex_id=%s, wing_id=%s, office_no=%s", complex_id, wing_id, office_no)

    #         partner.sudo().write({
    #             'complex_id': complex_id,
    #             'wing_id': wing_id,
    #             'office_no': office_no,
    #         })
    #     return response

    # @http.route(['/shop/address'], type='http', auth="public", website=True)
    # def shop_address(self, **kw):
    #     response = super().shop_address(**kw)
    #     if kw.get('partner_id'):
    #         partner = request.env['res.partner'].browse(int(kw['partner_id']))
    #         partner.sudo().write({
    #             'complex_id': int(kw.get('complex_id', 0)) or False,
    #             'wing_id': int(kw.get('wing_id', 0)) or False,
    #             'office_no': kw.get('office_no', ''),
    #             'region_id': kw.get('region_id', ''),  # Ensure region_id is stored
    #         })
    #     return response
    
    # @http.route(['/shop/address/submit'], type='json', auth="public", website=True)
    # def shop_address_submit(
    #     self, partner_id=None, address_type='billing', use_delivery_as_billing=None,
    #     callback=None, required_fields=None, **form_data
    # ):
    #     """Override submit function to include complex_id, wing_id, office_no"""
    #     response = super().shop_address_submit(
    #         partner_id=partner_id, address_type=address_type, use_delivery_as_billing=use_delivery_as_billing,
    #         callback=callback, required_fields=required_fields, **form_data
    #     )

    #     # Updating partner with custom fields
    #     partner_sudo = request.env['res.partner'].browse(int(partner_id))
    #     if partner_sudo:
    #         partner_sudo.sudo().write({
    #             'complex_id': int(form_data.get('complex_id', 0)) or False,
    #             'wing_id': int(form_data.get('wing_id', 0)) or False,
    #             'office_no': form_data.get('office_no', ''),
    #             'region_id': form_data.get('region_id', ''),
    #         })

    #     return response
    
    # @http.route('/get_wings', type='json', auth="public")
    # def get_wings(self, complex_id):
    #     complex_rec = request.env['res.partner.complex'].sudo().browse(int(complex_id))
    #     wings = complex_rec.wing_ids
    #     return [{'id': wing.id, 'name': wing.name} for wing in wings]

    # @http.route('/get_region', type='json', auth="public")
    # def get_region(self, complex_id):
    #     complex_rec = request.env['res.partner.complex'].sudo().browse(int(complex_id))
    #     return {'region_name': complex_rec.region_id.name if complex_rec.region_id else ''}


    # @http.route('/get_wings', type='json', auth="public")
    # def get_wings(self, complex_id):
    #     wings = request.env['res.partner.wing'].sudo().search([('id', 'in', request.env['res.partner.complex'].sudo().browse(int(complex_id)).wing_ids.ids)])
    #     return [{'id': wing.id, 'name': wing.name} for wing in wings]

    # @http.route('/get_region', type='json', auth="public")
    # def get_region(self, complex_id):        
    #     complex_rec = request.env['res.partner.complex'].sudo().browse(int(complex_id))
    #     return {'region_name': complex_rec.region_id.name if complex_rec.region_id else ''}

class WebsiteSaleCustom(WebsiteSale):

    def shop_address_submit(self, **kwargs):
        """Extend Odoo's shop_address_submit to store complex, wing, and region."""
        response = super().shop_address_submit(**kwargs)

        partner_id = int(kwargs.get('partner_id', 0))
        if partner_id:
            partner = request.env['res.partner'].sudo().browse(partner_id)
            complex_id = int(kwargs.get('complex_id', 0))
            wing_id = int(kwargs.get('wing_id', 0))
            region_id = int(kwargs.get('region_id', 0))

            partner.write({
                'complex_id': complex_id or False,
                'wing_id': wing_id or False,
                'region_id': region_id or False,
            })

        return response
    # ----------------------------------------------------
#     from odoo import http
# from odoo.http import request

# class WebsiteSaleCustom(http.Controller):

#     @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
#     def custom_cart_update(self, product_id, add_qty=1, meal_type=None, working_days=None, **kwargs):
#         order = request.website.sale_get_order(force_create=1)

#         # Convert working_days checkboxes to a list of IDs
#         if working_days:
#             if isinstance(working_days, str):  # Single value case
#                 working_days_ids = [int(working_days)]
#             elif isinstance(working_days, list):  # Multiple selected values
#                 working_days_ids = [int(day) for day in working_days]
#         else:
#             working_days_ids = []

#         # Add to cart with custom fields
#         order._cart_update(
#             product_id=int(product_id),
#             add_qty=int(add_qty),
#             set_qty=0,
#             attributes_values=[],
#             linked_line_id=None,
#             meal_type=meal_type,
#             working_day_ids=[(6, 0, working_days_ids)]
#         )

#         return request.redirect('/shop/cart')
