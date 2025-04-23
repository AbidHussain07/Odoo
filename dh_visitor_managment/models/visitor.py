from odoo import _,models,fields,api
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, timedelta,date
import base64
from random import randint
import random
import math
import qrcode
from io import BytesIO

class Visitor(models.Model):
    _name = 'visitor.partner'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    v_name = fields.Char(string="Visitor Name",required=True)
    partner_id = fields.Many2one('res.partner',string="Partner")
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Mobile")
    company_name = fields.Char(string="Company")
    phone = fields.Char(string="Phone")
    visitor_destination = fields.Many2one('res.users', string="Visitor Destination")
    visitor_type1 = fields.Many2one( 'visitor.type', string="Vistior Type")
    visitor_category_id = fields.Many2one('visitor.category',string="Visitor Category")
    check_in = fields.Datetime(string="Check In",copy=False) #, default=datetime.today())
    check_out = fields.Datetime(string="Check Out",copy=False)
    duration = fields.Float(string="Duration" ,compute="_compute_duration", store=True,copy=False)
    visitor_reject_reason = fields.Char(string="Reason")    
    refrence = fields.Char(related='department_id.name',string= "Reference")
    department_id = fields.Many2one('hr.department', string="Department")
    employee_id = fields.Many2one(related ='department_id.manager_id', string="Employee")
    responsible_person = fields.Many2one('res.users', string="Responsible Person" , required=True)
    otp = fields.Char(string='Otp', help="Login Otp" , reqiured=True)
    visitor_purpose = fields.Html(string="Note" , translate=True)
    name = fields.Char(string="No", required=True, copy=False, readonly=True, default='New')
    active = fields.Boolean(default=True) 
   
    qr_code = fields.Binary("QR Code" , readonly=True)
        
    visitor_checkin_gate_id = fields.Many2one('security.gates',string="Check in gate",copy=False)
    visitor_checkout_gate_id = fields.Many2one('security.gates',string="Check out gate",copy=False)
    checkin_guards_id = fields.Many2one('res.users', string="Security Checkin",copy=False) 
    checkout_guards_id = fields.Many2one('res.users', string="Security Checkout",copy=False) 
    
    
    


    VISITOR_STATE = [
    ('draft', 'Draft'),
    ('waiting', "Waiting"),
    ('approved', "Approved"),
    ('otp_verification', "Verified"),
    ('rejected', "Rejected"),
    ('done', "Done")]

    state = fields.Selection(
        selection=VISITOR_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True,default='draft')
    
   
    def action_print_pass(self):
        #after otp verification  we will print the visitor pass [state in verified]
        self.ensure_one()
        report_name = 'dh_visitor_managment.visitor_report_action'
        report_url = f'/report/pdf/{report_name}/{self.id}'
        return {
            'type': 'ir.actions.act_url',
            'url': report_url,
            'target': 'new', 
        }   

    def unlink(self):
        #only draft record we can delete no one other state record we can delete            
        for record in self:
            if record.state != 'draft':
                raise ValidationError(
                    "You can only delete visitor records in the 'Draft' state."
                )
        return super(Visitor, self).unlink()

            
    def generate_qr_code(self):
        #it can be genrate QR code 
        qr_config = {
            'version': 1,
            'error_correction': qrcode.constants.ERROR_CORRECT_L,
            'box_size': 3,
            'border': 4,
        }

        for rec in self:
            if not rec.name:
                rec.qr_code = False
                continue

            qr = qrcode.QRCode(**qr_config)
            qr.add_data(str(rec.name))
            
            qr.make(fit=True)

            with BytesIO() as temp:
                qr.make_image(fill_color="black", back_color="white").save(temp, format="PNG")
                rec.qr_code = base64.b64encode(temp.getvalue())


    @api.model
    def create(self, vals):
        #it can genrate  visitor ID ex.[E0001]
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('visitor.partner') or 'New'
        return super(Visitor, self).create(vals)    
        
   
    def action_waiting_visiitor(self):
        self.ensure_one()
        template = self.env.ref('dh_visitor_managment.visitor_email_template', raise_if_not_found=False)
        # when state in waiting  wizard will open and sending mail  
        if template:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mail.compose.message',
                'view_mode': 'form',
                'view_id': self.env.ref('mail.email_compose_message_wizard_form').id,
                'context': {
                        'default_model': 'visitor.partner',
                        'default_res_ids': [self.id],
                        'default_template_id': template.id,
                        'make_readonly': False,
                        'mark_as_waiting': True,
                        'default_partner_ids': [self.responsible_person.partner_id.id], 
                    },
                    'target': 'new',
            }
        

    @api.model
    def message_post(self, **kwargs):
        result = super().message_post(**kwargs)
        if self.env.context.get('mark_as_waiting'):
            self.filtered(lambda rec: rec.state != 'waiting').write({'state': 'waiting'})
        return result
          
    def action_approved_visiitor(self):
        #when the BYPASS otp is true otp genrating is skip
            if self.visitor_category_id and self.visitor_category_id.otp:
                self.write({'state': 'otp_verification'})
                self.message_post(body="visitor approved")

            else:
                self.write({'state': 'approved'})
                self.message_post(body="visitor approved")

            self.generate_qr_code()




    def action_reject_visiitor(self):
        #when state is an reject state wizard will open
        self.write({'state':'rejected'})
        for record in self:
            record.message_post(body="visitor Rejected")

        return {'type': 'ir.actions.act_window',
            'res_model': 'visitor.reject',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'wizard_type': "create"}, 
            }

    def action_draft_visiitor(self):
    # draft button on state
        self.write({'state': 'draft'})
        for record in self:
            record.message_post(body="visitor draft")

    def action_cancel_visiitor(self):
        self.write({'state': 'rejected'})
        return True

    def action_otp_verfication_visiitor(self):
        # open wizard for otp verification  [verifiy otp button]
        return {'type': 'ir.actions.act_window',
            'res_model': 'visitor.otp',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'otp':self.otp}, 
            }

    def action_send_otp(self):
        # send otp to the visitor via email otp will show in chatter
        digits = "0123456789"
        otp = ''.join(random.choices(digits, k=6))
        self.otp = otp
        template = self.env.ref('dh_visitor_managment.visitor_otp_verification', raise_if_not_found=False)
        if template:
            template.sudo().send_mail(self.id, force_send=True)

    @api.onchange('check_in')
    def _onchange_check_in(self):
        if self.check_in and self.check_in < datetime.now():
            self.check_in = datetime.now()


    @api.onchange('partner_id')
    def onchange_partner_id(self):
           # when the partner name  is changed then it is changed all the partner field value
        if self.partner_id:
            self.v_name = self.partner_id.name
            self.company_name = self.partner_id.company_id.name
            self.phone  = self.partner_id.phone
            self.mobile = self.partner_id.mobile
            self.email = self.partner_id.email

    def write(self, vals):
        for record in self:
            #res.partner will created
            partner = record.partner_id
            if 'partner_id' in vals:
                partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner:
                partner.write({
                    'name': vals.get('v_name') or record.v_name,
                    'phone': vals.get('phone') or record.phone,
                    'mobile': vals.get('mobile') or record.mobile,
                    'email': vals.get('email') or record.email,
                })
        return super(Visitor, self).write(vals)

    @api.depends('check_in', 'check_out')
    def _compute_duration(self):
        for record in self:
            if record.check_in and record.check_out:
                delta = record.check_out - record.check_in
                record.duration = delta.total_seconds() / 3600
            else:
                record.duration = 0.0

    def action_check_in(self):
        return {'type': 'ir.actions.act_window',
            'res_model': 'check.visitor',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {
                'default_visitor_id': self.name,
                'default_partner_id': self.id,
                'custom_wizard_type': "checkin"}
            }

    def action_check_out(self):
        return {'type': 'ir.actions.act_window',
            'res_model': 'check.visitor',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {
                'default_visitor_id': self.name,
                'default_partner_id': self.id,
                'custom_wizard_type': "checkout"}
            }