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

import base64
import json

from ast import literal_eval

from odoo import models, fields, api


class pos_cache(models.Model):
    _name = 'pos.cache'
    _description = 'Used to Store Product In POS Cache Memory.'

    cache = fields.Binary(attachment=True)
    product_domain = fields.Text(required=True)
    product_fields = fields.Text(required=True)

    config_id = fields.Many2one('pos.config', ondelete='cascade', required=True)
    compute_user_id = fields.Many2one('res.users', 'Cache compute user', required=True)

    @api.model
    def refresh_all_caches(self):
        self.env['pos.cache'].search([]).refresh_cache()

    @api.one
    def refresh_cache(self):
        Product = self.env['product.product'].sudo(self.compute_user_id.id)
        products = Product.search(self.get_product_domain())
        # products = Product.with_context({'location': self.config_id.stock_location_id.id}).search(
        #     self.get_product_domain())
        prod_ctx = products.with_context(pricelist=self.config_id.pricelist_id.id, display_default_code=False,
                                         lang=self.compute_user_id.lang)
        res = prod_ctx.read(self.get_product_fields())
        for each_rec in res:
            new_date = each_rec['write_date']
            each_rec['write_date'] = new_date.strftime('%Y-%m-%d %H:%M:%S')
        datas = {
            'cache': base64.encodestring(json.dumps(res).encode('utf-8')),
        }
        self.write(datas)

    @api.model
    def get_product_domain(self):
        return literal_eval(self.product_domain)

    @api.model
    def get_product_fields(self):
        return literal_eval(self.product_fields)

    @api.model
    def get_cache(self, domain, fields):
        if not self.cache or domain != self.get_product_domain() or fields != self.get_product_fields():
            self.product_domain = str(domain)
            self.product_fields = str(fields)
            self.refresh_cache()

        return json.loads(base64.decodestring(self.cache).decode('utf-8'))


class pos_config(models.Model):
    _inherit = 'pos.config'

    @api.one
    @api.depends('cache_ids')
    def _get_oldest_cache_time(self):
        pos_cache = self.env['pos.cache']
        oldest_cache = pos_cache.search([('config_id', '=', self.id)], order='write_date', limit=1)
        if oldest_cache:
            self.oldest_cache_time = oldest_cache.write_date

    # Use a related model to avoid the load of the cache when the pos load his config
    cache_ids = fields.One2many('pos.cache', 'config_id')
    oldest_cache_time = fields.Datetime(compute='_get_oldest_cache_time', string='Oldest cache time', readonly=True)

    def _get_cache_for_user(self):
        pos_cache = self.env['pos.cache']
        cache_for_user = pos_cache.search([('id', 'in', self.cache_ids.ids), ('compute_user_id', '=', self.env.uid)])

        if cache_for_user:
            return cache_for_user[0]
        else:
            return None

    @api.multi
    def get_products_from_cache(self, fields, domain):
        cache_for_user = self._get_cache_for_user()

        if cache_for_user:
            return cache_for_user.get_cache(domain, fields)
        else:
            pos_cache = self.env['pos.cache']
            pos_cache.create({
                'config_id': self.id,
                'product_domain': str(domain),
                'product_fields': str(fields),
                'compute_user_id': self.env.uid
            })
            new_cache = self._get_cache_for_user()
            return new_cache.get_cache(domain, fields)

    @api.one
    def delete_cache(self):
        # throw away the old caches
        self.cache_ids.unlink()

    @api.model
    def store_data_to_cache(self, data, prods):
        if data and data[0].get('product_domain'):
            data[0]['product_domain'] = str(data[0].get('product_domain'))
        if data and data[0].get('product_fields'):
            data[0]['product_fields'] = str(data[0].get('product_fields'))
        if data:
            pos_cache = self.env['pos.cache']
            res = pos_cache.create(data[0])
            if res:
                res.refresh_cache()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
