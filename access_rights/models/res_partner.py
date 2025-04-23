from odoo import fields, models,api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    department_ids = fields.Many2many(
        comodel_name='hr.department',
        string='Employee Departments',
        help='Select departments to access employees in these departments.'
    )

    customer_type = fields.Selection(
        selection=[
            ('vendor', 'Vendors'),
            ('customer', 'Customers'),
            ('other', 'Others'),
        ],
        string='Customer Type',
        default='other',
        help='Select the type of customer access for this user.'
    )

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    # Adding a new field to the hr.department model
    # department_code = fields.Char(string='Department Code')