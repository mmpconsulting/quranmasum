from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrContractAlloawnceRel(models.Model):
    _name = 'bp.hr.contract.allowance.rel'

    contract_id = fields.Many2one('hr.contract', string='Contract', required=True, )
    allowance_id = fields.Many2one('bp.hr.contract.allowance', string='Allowance', required=True, )
    code = fields.Char(related='allowance_id.code')
    amount = fields.Float(string='Amount', required=True, )

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount < 1:
                raise ValidationError('Amount must be greater than 0.')
