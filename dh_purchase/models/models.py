# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError
import re

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def create(self, vals):
        order = self.env['purchase.order'].browse(vals.get('order_id'))
        if order.state in ['purchase', 'done']:
            raise UserError(_("You cannot add products to a Purchase Order that is already confirmed."))
        return super(PurchaseOrderLine, self).create(vals)

    def write(self, vals):
        for line in self:
            if line.order_id.state in ['purchase', 'done']:
                raise UserError(_("You cannot modify products in a confirmed Purchase Order."))
        return super(PurchaseOrderLine, self).write(vals)



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('client_order_ref')
    def _onchange_client_order_ref(self):
        if self.client_order_ref:
            self.client_order_ref = self._format_reference(self.client_order_ref)

    @api.model
    def create(self, vals):
        if 'client_order_ref' in vals and vals['client_order_ref']:
            vals['client_order_ref'] = self._format_reference(vals['client_order_ref'])
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        if 'client_order_ref' in vals and vals['client_order_ref']:
            vals['client_order_ref'] = self._format_reference(vals['client_order_ref'])
        return super(SaleOrder, self).write(vals)

    def _format_reference(self, ref):
        parts = re.findall(r'[A-Za-z]+|\d+', ref) # [A-Za-z]+ --> start from A to Z, a to z till word end & [\d+] --> start from 0 to 9 till digit end
        return '-'.join(parts)
