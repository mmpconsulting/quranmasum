from math import ceil
from odoo import api, fields, models, _
from pprint import pprint

class accountinvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _default_company_id(self):
        user = self.env['res.users'].browse(self.env.uid)
        return user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Nama Perusahaan", default=_default_company_id)

    def recompute_coly(self):
        for line in self.invoice_line_ids:
            line._compute_coly()

    def get_ongkir(self):
        delivery_products = self.env['delivery.carrier'].search([('active','=',True)]).mapped('product_id')
        ongkir = sum(self.invoice_line_ids.filtered(lambda x :x.product_id.id in delivery_products.ids ).mapped('price_subtotal'))
        return ongkir


    def get_splitted_lines(self):
        loop_num = range(0, len(self.invoice_line_ids), self.env.user.company_id.line_per_page)

        splited_lines = []

        # filtered invoice line fom ongkir
        delivery_products = self.env['delivery.carrier'].search([('active','=',True)]).mapped('product_id')
        filtered_lines = self.invoice_line_ids.filtered(lambda x :x.product_id.id not in delivery_products.ids )

        for idx in loop_num:
            # splited_lines.append(self.invoice_line_ids[idx:idx+self.env.user.company_id.line_per_page])

            # with filtered ongkir
            splited_lines.append(filtered_lines[idx:idx+self.env.user.company_id.line_per_page])
            

        for pg in splited_lines:
            for line in pg:
                print(line.product_id.name)
            print('----------------------------------')

        return splited_lines

        # return ceil(len(self.invoice_line_ids) / self.env.user.company_id.line_per_page)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        # compute='_compute_prod_lots',
        string="Production Lot",
    )
    coly = fields.Char(string='Coly')
    total_coly = fields.Integer(compute='_compute_coly', string='Coly', store=True, inverse="_inverse_compute_coly")

    @api.depends('quantity')
    def _compute_coly(self):
        for rec in self:
            rec.total_coly = ceil(rec.quantity / (rec.product_id.qty_per_pack or 1)) or 1

    @api.depends('quantity')
    def _inverse_compute_coly(self):
        pass

    # def _compute_prod_lots(self):
    #     for line in self:
    #         line.lot_id = line.mapped(
    #             'move_line_ids.lot_id'
    #         )
