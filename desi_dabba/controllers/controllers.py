# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class DesiDabba(http.Controller):
    @http.route('/desi_dabba/desi_dabba', auth='public')
    def index(self, **kw):
        return "Hello, world"

#     @http.route('/desi_dabba/desi_dabba/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('desi_dabba.listing', {
#             'root': '/desi_dabba/desi_dabba',
#             'objects': http.request.env['desi_dabba.desi_dabba'].search([]),
#         })

#     @http.route('/desi_dabba/desi_dabba/objects/<model("desi_dabba.desi_dabba"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('desi_dabba.object', {
#             'object': obj
#         })

# class MyController(http.Controller):

#     @http.route('/get_wings', type='json', auth='public',website=True)
#     def get_wings(self, complex_id):
#         import pdb;pdb.set_trace()
#         # Sample data fetching logic
#         wings = request.env['wing.model'].sudo().search([('complex_id', '=', complex_id)])
#         return [{'id': wing.id, 'name': wing.name} for wing in wings]

#     @http.route('/get_region', type='json', auth='public')
#     def get_region(self, complex_id):
#         import pdb;pdb.set_trace()
#         # Sample data fetching logic
#         complex = request.env['complex.model'].sudo().browse(complex_id)
#         return {'region_name': complex.region.name if complex.region else ''}