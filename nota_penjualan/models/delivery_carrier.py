from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    is_manual_input = fields.Boolean("Manual Input ?", default=False)
