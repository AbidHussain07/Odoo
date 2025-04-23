# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    cancel_days = fields.Integer(string='Cancellation Before' , default=1, config_parameter='hospital.cancel_days' )
    # config_parameter is used to store the value in the database 
