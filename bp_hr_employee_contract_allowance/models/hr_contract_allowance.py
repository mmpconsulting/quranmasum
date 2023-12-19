from odoo import models, fields, api


class HrContractAllowance(models.Model):
    _name = 'bp.hr.contract.allowance'

    name = fields.Char(string='Name', required=True, )
    code = fields.Char(string='Code', required=True)
    contract_ids = fields.One2many('bp.hr.contract.allowance.rel', 'allowance_id', string='Contracts')

    _sql_constraints = [
        ('allowance_code', 'unique(code)', 'Allowance must be unique.')
    ]
