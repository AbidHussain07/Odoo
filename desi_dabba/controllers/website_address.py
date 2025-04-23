from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleExtended(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        fields = super()._get_mandatory_billing_fields()
        fields.extend(['complex_id', 'wing_id', 'office_no', 'region_id'])
        return fields

    def _get_mandatory_shipping_fields(self):
        fields = super()._get_mandatory_shipping_fields()
        fields.extend(['complex_id', 'wing_id', 'office_no', 'region_id'])
        return fields

    @http.route(['/shop/address'], type='http', auth="public", website=True)
    def shop_address(self, **kw):
        """ Override to ensure custom fields are prefilled in the form """
        response = super().shop_address(**kw)

        if 'partner_id' in kw and kw['partner_id']:
            partner = request.env['res.partner'].sudo().browse(int(kw['partner_id']))
            if partner.exists():
                response.qcontext.update({
                    'complex_id': partner.complex_id.id if partner.complex_id else False,
                    'wing_id': partner.wing_id.id if partner.wing_id else False,
                    'office_no': partner.office_no or '',
                    'region_id': partner.region_id.id if partner.region_id else False,
                })

        return response

    @http.route(['/shop/address/submit'], type='json', auth="public", website=True)
    def shop_address_submit(self, partner_id=None, address_type='billing', **form_data):
        """ Override submit function to ensure complex_id, wing_id, office_no, and region_id are saved """
        response = super().shop_address_submit(partner_id=partner_id, address_type=address_type, **form_data)

        partner_values = {
            'complex_id': int(form_data.get('complex_id', 0)) or False,
            'wing_id': int(form_data.get('wing_id', 0)) or False,
            'office_no': form_data.get('office_no', ''),
            'region_id': int(form_data.get('region_id', 0)) or False,
        }

        if partner_id:
            partner_sudo = request.env['res.partner'].browse(int(partner_id))
            partner_sudo.sudo().write(partner_values)
        else:
            new_partner = request.env['res.partner'].sudo().create(partner_values)
            response['partner_id'] = new_partner.id 

        return response
    
    @http.route('/get_wings', type='json', auth="public")
    def get_wings(self, complex_id):
        complex_rec = request.env['res.partner.complex'].sudo().browse(int(complex_id))
        wings = complex_rec.wing_ids
        return [{'id': wing.id, 'name': wing.name} for wing in wings]

    @http.route('/get_region', type='json', auth="public")
    def get_region(self, complex_id):
        complex_rec = request.env['res.partner.complex'].sudo().browse(int(complex_id))
        return {'region_id': complex_rec.region_id.id if complex_rec.region_id else False}
