from odoo import models, fields

class TiffinHoliday(models.Model):
    _name = 'tiffin.holiday'
    _description = 'Holiday Dates for Tiffin Delivery'
    _order = 'date'

    name = fields.Char(string='Holiday Name', required=True)
    date = fields.Date(string='Holiday Date', required=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    meal_type = fields.Selection([
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ], string="Meal Type")

    working_day_ids = fields.Many2many("working.days", string="Working Days")