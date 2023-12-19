# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = "stock.picking"

    total_product_of_delivery_orders = fields.Integer(string='Total Product:',compute='_total_product_of_delivery_orders',help="total Products of delivery orders")
    total_quantity_of_delivery_orders = fields.Integer(string='Reserved Quantity:',compute='_total_quantity_of_delivery_orders',help="total Quantity of delivery orders")
    total_quantity_of_delivery_orders_done = fields.Integer(string='Done Quantity:',compute='_total_quantity_of_delivery_orders',help="total Quantity of delivery orders")

    def _total_product_of_delivery_orders(self):
        for record in self:
            list_of_delivery_product=[]
            for line in record.move_lines:
                list_of_delivery_product.append(line.product_id)
            record.total_product_of_delivery_orders = len(set(list_of_delivery_product))

    def _total_quantity_of_delivery_orders(self):
        for record in self:
            total_qty = 0
            total_qty_done = 0
            for line in record.move_lines:
                total_qty = total_qty + line.product_uom_qty
                total_qty_done = total_qty_done + line.quantity_done
            record.total_quantity_of_delivery_orders = total_qty
            record.total_quantity_of_delivery_orders_done = total_qty_done

