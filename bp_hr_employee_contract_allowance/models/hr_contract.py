from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    allowance_ids = fields.One2many('bp.hr.contract.allowance.rel', 'contract_id', string='Allowances')

    def allowance_amount(self, code):
        return self.allowance_ids.filtered(lambda x: x.code == code).amount
