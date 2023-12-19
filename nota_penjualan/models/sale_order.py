from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_price = fields.Float(string='Estimated Delivery Price', readonly=False, copy=False)
    is_manual_input = fields.Boolean(related='carrier_id.is_manual_input')

    def get_delivery_price(self):
        if self.carrier_id.is_manual_input:
            # bypass delivery price to order line
            for order in self.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
                order.delivery_rating_success = True
                order.delivery_price = self.delivery_price
                # order.delivery_message = "Success"

            self.set_delivery_line()
        else:
            super(SaleOrder, self).get_delivery_price()

    def _create_delivery_line(self, carrier, price_unit):
        if carrier.is_manual_input:
            price_unit = self.delivery_price

        super(SaleOrder, self)._create_delivery_line(carrier, price_unit)

