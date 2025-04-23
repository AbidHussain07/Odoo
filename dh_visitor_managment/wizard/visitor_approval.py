from odoo import fields, models,api,_
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, timedelta,date


class VisitorReject(models.TransientModel):
    _name = 'visitor.reject'
    _description = "visitor reject wizard"

  
    rejection_reason = fields.Char("Reason")

   
    def action_reject_visitor(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            visitor = self.env['visitor.partner'].browse(active_id)
            visitor.write({'visitor_reject_reason': self.rejection_reason})



class VisitorOtp(models.TransientModel):
    _name = 'visitor.otp'
    _description = "Visitor Verification Otp"


    verification_otp = fields.Char("OTP" , size=6)

    @api.constrains('verification_otp')
    def _otp_length(self):
        for record in self:
            if not (6 <= len(record.verification_otp)):
                raise ValidationError(_("OTP must be in 6 Digit"))


    def verify_otp(self):
        visitor_partner = self.env['visitor.partner'].browse(self.env.context.get('active_id'))
        if self.env.context.get('otp') == self.verification_otp:
            visitor_partner.state = 'otp_verification'
            visitor_partner.message_post(body="visitor verified successfully!!")
        else :
            raise UserError(_("Please enter valid OTP"))
        


class CheckVisitor(models.TransientModel):
    _name = 'check.visitor'
    _description = "Visitor CheckIN Checkout"


    validated_qr_code = fields.Boolean(string="Validate code")
    visitor_name = fields.Char(related='partner_id.name',string="Visitor Name")

    visitor_id =fields.Char(string="Visitor" , readonly=True) 
    partner_id = fields.Many2one('visitor.partner', string="Visitor", required=True)
    gate_number_id = fields.Many2one('security.gates', string="Gate Number") 
    security_guard_id = fields.Many2one('res.users', string="Security Guard Name") 
    
    
    
    @api.model
    def default_get(self, fields):
        res = super(CheckVisitor, self).default_get(fields)
        user = self.env.user
        assigned_gates = self.env['security.gates'].search([('security_guard_ids', 'in', user.id)])
        if assigned_gates:
            res['gate_number_id'] = assigned_gates.id
            res['security_guard_id'] = user.id
            
        return res
    


    def action_validate_qr(self):        
        visitor_id = self.env.context.get('active_id')       
        visitor = self.env['visitor.partner'].browse(visitor_id)
        wizard_type = self.env.context.get('custom_wizard_type')
        
        
        if not self.validated_qr_code and self.env.context.get('custom_wizard_type') != 'validate':
            raise ValidationError("Scan your Qr code")     
        
        if self.partner_id and (self.validated_qr_code or wizard_type == 'validate'):
            if not self.partner_id.check_in:
                self.partner_id.check_in = datetime.now()
                if self.gate_number_id:
                        self.partner_id.visitor_checkin_gate_id = self.gate_number_id 
                if self.security_guard_id:
                        self.partner_id.checkin_guards_id = self.security_guard_id 
            elif not self.partner_id.check_out:
                self.partner_id.check_out = datetime.now()
                self.partner_id.state = 'done'
                if self.gate_number_id:
                    self.partner_id.visitor_checkout_gate_id = self.gate_number_id
                if self.security_guard_id:
                        self.partner_id.checkout_guards_id = self.security_guard_id 
     
    


        elif visitor and self.validated_qr_code:
            if not visitor.check_in:
                visitor.check_in = datetime.now()
            if self.gate_number_id: 
                visitor.visitor_checkin_gate_id = self.gate_number_id
            if self.security_guard_id:
                        self.partner_id.visitor_checkin_gate_id = self.security_guard_id 
            elif not visitor.check_out:
                visitor.check_out = datetime.now()
                visitor.visitor_checkout_gate_id = self.gate_number_id
                self.partner_id.checkout_guards_id = self.security_guard_id 
    

                
class VisitorReporting(models.TransientModel):
    _name = 'visitor.reporting'
    _description = "Visitor Reporting"
    
    
    checkin = fields.Datetime(string="From", required=True)
    checkout = fields.Datetime(string="To", required=True)
    responsible_persons = fields.Many2one('res.users', string="Responsible Person")
    gate_number_id = fields.Many2one('security.gates', string="Gate Number") 
    

    def action_visitor_reporting_detail(self):
        domain = []
        if self.checkin:
            domain.append(('check_in', '>=', self.checkin))
        if self.checkout:
            domain.append(('check_out', '<=', self.checkout))
        if self.responsible_persons:
            domain.append(('responsible_person', '=', self.responsible_persons.id))
        if self.gate_number_id:
            domain.append(('visitor_checkout_gate_id', '=', self.gate_number_id.id))

        visitors = self.env['visitor.partner'].search(domain)

        return self.env.ref('dh_visitor_managment.action_report_visitor_pdf').report_action(visitors)
