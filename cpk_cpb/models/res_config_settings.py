# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bahan_awal_categ_name = fields.Many2many('product.category', 'categ_bahan_awal_rel', string="Categ Bahan Awal")
    bahan_pengemas_categ_name = fields.Many2many('product.category', 'categ_bahan_pengemas_rel', string="Categ Bahan Pengemas")
    bahan_kemas_sekunder_categ_name = fields.Many2many('product.category', 'categ_bahan_kemas_sekunder_rel', string="Categ Bahan Kemas Sekunder")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('cpk_cpb.default_categ_bahan_awal', self.bahan_awal_categ_name.ids)
        self.env['ir.config_parameter'].set_param('cpk_cpb.default_categ_bahan_pengemas', self.bahan_pengemas_categ_name.ids)
        self.env['ir.config_parameter'].set_param('cpk_cpb.default_categ_bahan_kemas_sekunder', self.bahan_kemas_sekunder_categ_name.ids)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        CcSudo = self.env['ir.config_parameter'].sudo()
        bahan_awal_categ_name = CcSudo.get_param('cpk_cpb.default_categ_bahan_awal')
        bahan_pengemas_categ_name = CcSudo.get_param('cpk_cpb.default_categ_bahan_pengemas')
        bahan_kemas_sekunder_categ_name = CcSudo.get_param('cpk_cpb.default_categ_bahan_kemas_sekunder')
        res.update(
            bahan_awal_categ_name=[(6, 0, literal_eval(bahan_awal_categ_name))] if bahan_awal_categ_name else False,
            bahan_pengemas_categ_name=[(6, 0, literal_eval(bahan_pengemas_categ_name))] if bahan_pengemas_categ_name else False,
            bahan_kemas_sekunder_categ_name=[(6, 0, literal_eval(bahan_kemas_sekunder_categ_name))] if bahan_kemas_sekunder_categ_name else False,
        )
        return res
    