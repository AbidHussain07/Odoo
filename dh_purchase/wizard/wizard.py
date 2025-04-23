from odoo import models, fields, api
from odoo.exceptions import UserError

class BulkInvoiceWizard(models.TransientModel):
    _name = 'bulk.invoice.wizard'
    _description = 'Wizard to send bulk invoices by email'

    invoice_ids = fields.Many2many('account.move', string='Invoices', domain=[('move_type', '=', 'out_invoice')])
    mail_template_id = fields.Many2one('mail.template', string='Mail Template')

    def send_invoices(self):
        if not self.mail_template_id:
            raise UserError('Please select a mail template.')

        for invoice in self.invoice_ids:
            if not invoice.partner_id.email:
                continue
            self.mail_template_id.send_mail(invoice.id, force_send=True)

        return {'type': 'ir.actions.act_window_close'}
