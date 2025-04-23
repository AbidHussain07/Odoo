from odoo import models, api, fields

class PatientTag(models.Model):
    _name = 'patient.tag'
    _description = "Patient Tags"
    _order = "sequence,id"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color Index")
    color2 = fields.Char(string="Color")
    sequence = fields.Integer(default='1')
    
    # only fo understanding of copy method
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = '%s (copy)' % self.name
        default['sequence'] = 10
        return super (PatientTag, self).copy(default)

    _sql_constraints = [('unique_name', "unique(name)", "This Disease already exists in the database."),
                        # only for understanding of check constraint
                        # ('check_sequence', "check(sequence < 0)", " Sequence must be positive.")
                        ]
