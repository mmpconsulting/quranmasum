#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

import ast

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def load_rfid_settings(self):
        record = {}
        settings_is_rfid_login = self.env['ir.config_parameter'].sudo().search([('key', '=', 'is_rfid_login')])
        if settings_is_rfid_login:
            record['is_rfid_login'] = settings_is_rfid_login.value
            return [record]

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter'].sudo()
        res_user_ids = param_obj.sudo().get_param('res_user_ids')
        if res_user_ids:
            res.update({'res_user_ids': ast.literal_eval(res_user_ids)})

        res.update(
            google_api_key=param_obj.get_param('google_api_key'),
            theme_selector=param_obj.get_param('theme_selector'),
            gen_barcode=param_obj.get_param('gen_barcode'),
            barcode_selection=param_obj.get_param('barcode_selection'),
            gen_internal_ref=param_obj.get_param('gen_internal_ref'),
            mailsend_check=param_obj.get_param('mailsend_check'),
            email_notification_days=int(param_obj.sudo().get_param('email_notification_days')),
            is_rfid_login=param_obj.get_param('is_rfid_login'),
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param_obj = self.env['ir.config_parameter'].sudo()
        param_obj.set_param('google_api_key', self.google_api_key or '')
        param_obj.set_param('theme_selector', self.theme_selector or False)
        param_obj.set_param('gen_barcode', self.gen_barcode)
        param_obj.set_param('barcode_selection', self.barcode_selection)
        param_obj.set_param('gen_internal_ref', self.gen_internal_ref)
        param_obj.set_param('mailsend_check', self.mailsend_check)
        param_obj.set_param('res_user_ids', self.res_user_ids.ids)
        param_obj.set_param('email_notification_days', self.email_notification_days)
        param_obj.set_param('is_rfid_login', self.is_rfid_login or False)
        return res

    google_api_key = fields.Char('Google API key')
    theme_selector = fields.Selection(
        [('green_orange', 'Green Orange'), ('blue_yellow', 'Blue Yellow'), ('purple_blue', 'Purple Blue')])
    gen_barcode = fields.Boolean("On Product Create Generate Barcode")
    barcode_selection = fields.Selection([('code_39', 'CODE 39'), ('code_128', 'CODE 128'),
                                          ('ean_13', 'EAN-13'), ('ean_8', 'EAN-8'),
                                          ('isbn_13', 'ISBN 13'), ('isbn_10', 'ISBN 10'),
                                          ('issn', 'ISSN'), ('upca', 'UPC-A')], string="Select Barcode Type")
    gen_internal_ref = fields.Boolean(string="On Product Create Generate Internal Reference")
    mailsend_check = fields.Boolean(string="Send Mail")
    email_notification_days = fields.Integer(string="Expiry Alert Days")
    res_user_ids = fields.Many2many('res.users', string='Users')
    is_rfid_login = fields.Boolean("RFID Pos Login")


class res_company(models.Model):
    _inherit = "res.company"

    pos_price = fields.Char(string="Pos Price", size=1)
    pos_quantity = fields.Char(string="Pos Quantity", size=1)
    pos_discount = fields.Char(string="Pos Discount", size=1)
    pos_search = fields.Char(string="Pos Search", size=1)
    pos_next = fields.Char(string="Pos Next order", size=1)
    payment_total = fields.Char(string="Payment", size=1)
    report_ip_address = fields.Char(string="Thermal Printer Proxy IP")
    shop_ids = fields.Many2many("pos.store", 'pos_shop_company_rel', 'shop_id', 'company_id', string='Allow Shops')

    @api.one
    def write(self, vals):
        current_shop_ids = self.shop_ids
        res = super(res_company, self).write(vals)
        if 'shop_ids' in vals:
            current_shop_ids -= self.shop_ids
            for shop in current_shop_ids:
                shop.company_id = False
            for shop in self.shop_ids:
                shop.company_id = self
        return res


class res_partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def loyalty_reminder(self):
        partner_ids = self.search([('email', "!=", False), ('send_loyalty_mail', '=', True)])
        for partner_id in partner_ids.filtered(lambda partner: partner.remaining_loyalty_points > 0):
            try:
                template_id = self.env['ir.model.data'].get_object_reference('flexiretail_com_advance',
                                                                             'email_template_loyalty_reminder')
                template_obj = self.env['mail.template'].browse(template_id[1])
                template_obj.send_mail(partner_id.id, force_send=True, raise_exception=False)
            except Exception as e:
                _logger.error('Unable to send email for order %s', e)

    @api.multi
    def _calculate_earned_loyalty_points(self):
        loyalty_point_obj = self.env['loyalty.point']
        for partner in self:
            total_earned_points = 0.00
            for earned_loyalty in loyalty_point_obj.search([('partner_id', '=', partner.id)]):
                total_earned_points += earned_loyalty.points
            partner.loyalty_points_earned = total_earned_points

    @api.multi
    def _calculate_remaining_loyalty(self):
        loyalty_point_obj = self.env['loyalty.point']
        loyalty_point_redeem_obj = self.env['loyalty.point.redeem']
        for partner in self:
            points_earned = 0.00
            amount_earned = 0.00
            points_redeemed = 0.00
            amount_redeemed = 0.00
            for earned_loyalty in loyalty_point_obj.search([('partner_id', '=', partner.id)]):
                points_earned += earned_loyalty.points
                amount_earned += earned_loyalty.amount_total
            for redeemed_loyalty in loyalty_point_redeem_obj.search([('partner_id', '=', partner.id)]):
                points_redeemed += redeemed_loyalty.redeemed_point
                amount_redeemed += redeemed_loyalty.redeemed_amount_total
            partner.remaining_loyalty_points = points_earned - points_redeemed
            partner.remaining_loyalty_amount = amount_earned - amount_redeemed
            partner.total_remaining_points = points_earned - points_redeemed

    #             partner.sudo().write({
    #                 'total_remaining_points': points_earned - points_redeemed
    #             })

    loyalty_points_earned = fields.Float(compute='_calculate_earned_loyalty_points')
    remaining_loyalty_points = fields.Float("Remaining Loyalty Points", readonly=1,
                                            compute='_calculate_remaining_loyalty')
    remaining_loyalty_amount = fields.Float("Points to Amount", readonly=1, compute='_calculate_remaining_loyalty')
    send_loyalty_mail = fields.Boolean("Send Loyalty Mail", default=True)
    total_remaining_points = fields.Float("Total Loyalty Points", readonly=1, compute='_calculate_remaining_loyalty')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
