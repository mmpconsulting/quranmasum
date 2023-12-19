from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qty_per_pack = fields.Integer(string='Quantity/Pack (Coly)', default=1)

    