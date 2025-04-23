from odoo import models
import base64
import io

class PatientCardXlsx(models.AbstractModel):
    _name = 'report.hospital.report_patient_card_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Excel Report of Patient"

    def generate_xlsx_report(self, workbook, data, patients):
        if not patients:
            raise ValueError("No patient data found for generating report.")
        bold = workbook.add_format({'bold': True})
        format_1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'yellow'})

        for obj in patients:
            sheet = workbook.add_worksheet(obj.name)
            row = 3
            col = 3
            sheet.set_column('D:D', 12)
            sheet.set_column('E:E', 13)

            row += 1
            sheet.merge_range(row, col, row, col + 1, 'ID Card', format_1)

            row += 1
            if obj.patient_image:
                image = io.BytesIO(base64.b64decode(obj.patient_image))
                sheet.insert_image(row, col, "image.png", {'image_data': image, 'x_scale': 1, 'y_scale': 1})

                row += 6
            sheet.write(row, col, 'Name', bold)
            sheet.write(row, col + 1, obj.name)
            row += 1
            sheet.write(row, col, 'Gender', bold)
            sheet.write(row, col + 1, obj.gender)
            row += 1
            sheet.write(row, col, 'Age', bold)
            sheet.write(row, col + 1, obj.age)

            row += 2
            sheet.merge_range(row, col, row + 1, col + 1, '', format_1)




