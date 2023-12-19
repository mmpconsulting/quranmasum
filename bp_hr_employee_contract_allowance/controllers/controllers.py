# -*- coding: utf-8 -*-
from odoo import http

# class BpHrEmployeeContractAllowance(http.Controller):
#     @http.route('/bp_hr_employee_contract_allowance/bp_hr_employee_contract_allowance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bp_hr_employee_contract_allowance/bp_hr_employee_contract_allowance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bp_hr_employee_contract_allowance.listing', {
#             'root': '/bp_hr_employee_contract_allowance/bp_hr_employee_contract_allowance',
#             'objects': http.request.env['bp_hr_employee_contract_allowance.bp_hr_employee_contract_allowance'].search([]),
#         })

#     @http.route('/bp_hr_employee_contract_allowance/bp_hr_employee_contract_allowance/objects/<model("bp_hr_employee_contract_allowance.bp_hr_employee_contract_allowance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bp_hr_employee_contract_allowance.object', {
#             'object': obj
#         })