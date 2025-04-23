from odoo import models, fields,api

class ResPartnerRegion(models.Model):
    _name = 'res.partner.region'
    _description = 'Region'

    name = fields.Char(string="Region Name", required=True)

class ResPartnerComplex(models.Model):
    _name = 'res.partner.complex'
    _description = 'Residential Complex'
    
    name = fields.Char(string="Complex Name", required=True)
    region_id = fields.Many2one('res.partner.region', string="Region")
    wing_ids = fields.Many2many('res.partner.wing', string="Wings")


class ResPartnerWing(models.Model):
    _name = 'res.partner.wing'
    _description = 'Complex Wings'

    name = fields.Char(string="Wing Name", required=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    complex_id = fields.Many2one('res.partner.complex', string="Complex",required=True)
    wing_id = fields.Many2one('res.partner.wing', string="Wing",required=True)
    office_no = fields.Char(string="Office No.",required=True)
    region_id = fields.Many2one('res.partner.region', string="Region")

    @api.onchange('complex_id')
    def _onchange_complex_id(self):
        self.region_id = self.complex_id.region_id