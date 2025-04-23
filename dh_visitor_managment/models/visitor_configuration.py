from odoo import _,models,fields,api
from odoo.exceptions import ValidationError,UserError


class VisitorCategory(models.Model):
    _name = 'visitor.category'
    _description = 'Visitor visit Record'
   
    name = fields.Char("Name", required=True)
    otp = fields.Boolean("Bypass otp" , default=False)

   
class VisitorType(models.Model):
    _name = 'visitor.type'
    _description = 'Visitor Type '

    name = fields.Char("Name",required=True)
    

class Gates(models.Model):
    _name = 'security.gates'
    _description = 'Security Gates'

    name = fields.Char("Name" , required=True)    
    security_guard_ids = fields.Many2many('res.users', string="Security Guard Name") 


    
    @api.constrains('security_guard_ids')
    def _check_security_guard(self):
        for record in self:
            for guard in record.security_guard_ids:
                other_gate = self.search([
                    ('id', '!=', record.id),
                    ('security_guard_ids', 'in', guard.id)
                ], limit=1)
                if other_gate:
                    raise ValidationError(f"Please select another guard. {guard.name} is already assigned to {other_gate.name}.")