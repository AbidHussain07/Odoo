from odoo import http
from odoo.http import request

class HospitalController(http.Controller):

    # @http.route('/learning', auth='public')
    # def display_data(self, **kwargs):
    #     return 'Hello World! I am Learning Controller for the first time.'

    # To get only integer to find id or anything
    @http.route('/learning/<int:id>', auth='public')
    def display_data(self, id):
        return '<h1>{}</h1>'.format(type(id).__name__)
    
    # ======================================================================================================

    @http.route('/hospital/patients', auth='public', website=True)
    def list_patients(self, **kwargs):
        patients = request.env['hospital.patient'].search([])
        return request.render('hospital.record_of_patient', {
            'patients': patients
        })

    @http.route('/hospital/patient/<model("hospital.patient"):patient>', auth='public', website=True)
    def patient_detail(self, patient, **kwargs):
        return request.render('hospital.patient_detail_template', {
            'patient': patient
        })