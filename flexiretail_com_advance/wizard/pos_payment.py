# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models, api, _
from odoo.exceptions import Warning
from odoo.tools import float_is_zero


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    @api.multi
    def check(self):
        """Check the order:
        if the order is not paid: continue payment,
        if the order is paid print ticket.
        """
        self.ensure_one()
        order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
        currency = order.pricelist_id.currency_id
        amount = order.amount_total - order.amount_paid
        data = self.read()[0]
        # add_payment expect a journal key
        data['journal'] = data['journal_id'][0]
        data['amount'] = currency.round(data['amount']) if currency else data['amount']
        if order.session_id.state == 'closed' and order.delivery_user_id:
            active_session_id = self.env['pos.session'].search([('state', '=', 'opened'),
                                                                ('user_id', '=', order.session_id.user_id.id)], limit=1)
            if not active_session_id and order.delivery_user_id.open_session_during_delivery:
                order.config_id.current_session_id = self.env['pos.session'].sudo().create({
                    'user_id': order.session_id.user_id.id,
                    'config_id': order.config_id.id
                })
            elif not self.session_id.user_id.open_session_during_delivery:
                raise Warning(_("You need to have at least one open session for delivery payment !"))
        if self._context.get('modify_payment'):
            order.add_payment(data)
        if not float_is_zero(amount, precision_rounding=currency.rounding or 0.01):
            order.add_payment(data)
        if order.test_paid():
            order.action_pos_order_paid()
            return {'type': 'ir.actions.act_window_close'}
        return self.launch_payment()
