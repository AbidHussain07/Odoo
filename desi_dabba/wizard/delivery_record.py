from odoo import models, fields, api
from datetime import timedelta,datetime,time
from io import BytesIO
import xlsxwriter
import base64

class ReportDeliveryWizard(models.TransientModel):
    _name = 'daily.report.delivery.wizard'
    _description = 'Report of Daily Delivery '

    date_report = fields.Date(string='Date', required=True, default=fields.Date.today)
    type_of_meal = fields.Selection([('lunch', 'Lunch'), ('dinner', 'Dinner')], string='Type of Meal', required=True)

    # def action_delivery_pdf_print(self):
    #     return self.env.ref('desi_dabba.action_report_delivery_daily').report_action(self)
    
    def action_delivery_pdf_print(self):
        return self.env.ref('desi_dabba.action_report_delivery_daily').report_action(self)
    
            
    def action_delivery_excel_print(self):

        pickings = self.env['stock.picking'].search([
            ('schedule_date', '=', self.date_report),
            ('meal_type', '=', self.type_of_meal)
        ])
        pickings = sorted(pickings, key=lambda p: (
            p.partner_id.region_id.id,
            p.partner_id.complex_id.id,
            p.partner_id.wing_id.id,
            p.partner_id.office_no or ''
        ))

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Delivery Report')

        title_format = workbook.add_format({
            'bold': True, 'font_size': 14,
            'align': 'center', 'valign': 'vcenter'
        })
        group_format = workbook.add_format({
            'bold': True, 'bg_color': '#D9E1F2',
            'align': 'center', 'valign': 'vcenter'
        })
        bold = workbook.add_format({'bold': True})

        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 25) 
        worksheet.set_column(2, 2, 25)  
        worksheet.set_column(3, 3, 15)  
        worksheet.set_column(4, 4, 20)  
        row = 0

        worksheet.merge_range(row, 0, row, 4, 'Delivery Report for {}'.format(self.date_report.strftime('%Y-%m-%d')), title_format)
        row += 2

        headers = ['Reference', 'Partner', 'Product', 'Office No.', 'Scheduled Date']

        current_region = None
        current_complex = None
        current_wing = None

        for picking in pickings:
            region = picking.partner_id.region_id
            complex_ = picking.partner_id.complex_id
            wing = picking.partner_id.wing_id

            if (region != current_region or complex_ != current_complex or wing != current_wing):
                if current_region:
                    row += 1  # Add spacing before new group

                group_title = 'Region: {} | Complex: {} | Wing: {}'.format(
                    region.name if region else 'N/A',
                    complex_.name if complex_ else 'N/A',
                    wing.name if wing else 'N/A',
                )
                worksheet.merge_range(row, 0, row, 4, group_title, group_format)
                row += 1

                # Write headers
                for col, header in enumerate(headers):
                    worksheet.write(row, col, header, bold)
                row += 1

                current_region = region
                current_complex = complex_
                current_wing = wing

            worksheet.write(row, 0, picking.name)
            worksheet.write(row, 1, picking.partner_id.name or '')
            worksheet.write(row, 2, picking.product_id.name or '')
            worksheet.write(row, 3, picking.partner_id.office_no or 'N/A')
            worksheet.write(row, 4, str(picking.schedule_date))
            row += 2

        workbook.close()
        output.seek(0)

        filename = 'Delivery_Report_{}.xlsx'.format(self.date_report.strftime('%Y-%m-%d'))
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': 'daily.report.delivery.wizard',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        download_url = '/web/content/{}/?download=true'.format(attachment.id)
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'self',
        }
