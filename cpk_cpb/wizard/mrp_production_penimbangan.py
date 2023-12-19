from odoo import models, fields, api
from odoo.addons.cpk_cpb.models.mrp_production import PENGOLAHAN_STATE_ORDER


class MrpProductionPenimbangan(models.Model):
    _name = 'mrp.production.penimbangan'
    _description = 'MRP Production Penimbangan'

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionPenimbangan, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            if 'production_id' in fields:
                res['production_id'] = production.id
                # res['alat_ids'] = [(6, 0, production.alat_ids.mapped('alat_id').ids)]
            raw_penimbangan = []
            for move in production.move_raw_bahan_awal_ids:
                raw_penimbangan.append((0, False, {
                    'product_id': move.product_id.id,
                    'jumlah_teoritis': move.product_uom_qty,
                    'product_uom': move.product_uom.id,
                    'move_id': move.id
                }))
            if raw_penimbangan:
                res['move_raw_ids'] = raw_penimbangan
        return res

    production_id = fields.Many2one('mrp.production', ondelete='cascade')

    date = fields.Datetime()

    @api.depends('production_id.alat_ids')
    def _compute_alat_ids(self):
        for rec in self:
            rec.alat_ids = [(6, 0, rec.production_id.alat_ids.mapped('alat_id').ids)]

    alat_ids = fields.Many2many('mrp.alat.ruang', string='timbang all', compute='_compute_alat_ids')
    alat_id = fields.Many2one('mrp.alat.ruang', domain="[('id', 'in', alat_ids)]")

    @api.onchange('alat_id')
    def _onchange_alat_id(self):
        line_alat = self.production_id.alat_ids.filtered(lambda line: line.alat_id.id == self.alat_id.id)
        self.protap_id = line_alat.protap_id.id

    protap_id = fields.Many2one('protap.protap')

    pelaksana = fields.Many2one('res.users')
    pemeriksa = fields.Many2one('res.users')

    # lines
    move_raw_ids = fields.One2many('stock.move.penimbangan', 'penimbangan_id', 'Bahan', copy=False)

    @api.model
    def create(self, vals):
        obj = super(MrpProductionPenimbangan, self).create(vals)
        obj.production_id.write({
            'penimbangan_id': obj.id
        })
        return obj 

    @api.multi
    def write(self, vals):
        res = super(MrpProductionPenimbangan, self).write(vals)
        for rec in self:
            if not rec.production_id.penimbangan_id:
                rec.production_id.write({
                    'penimbangan_id': rec.id
                })
        return res

    @api.multi
    def confirm(self):
        self.ensure_one()
        self.production_id.change_state(PENGOLAHAN_STATE_ORDER)
        return {'type': 'ir.actions.act_window_close'}


class StockMovePenimbangan(models.Model):
    _name = 'stock.move.penimbangan'
    _description = 'Stock Move Penimbangan'

    penimbangan_id = fields.Many2one('mrp.production.penimbangan', ondelete='cascade')

    product_id = fields.Many2one('product.product', copy=False, required=True)
    jumlah_teoritis = fields.Float('Jumlah Teoritis', copy=False)
    jumlah_nyata = fields.Float('Jumlah Nyata', copy=False)
    nomor_bets = fields.Many2one('stock.production.lot', string='No. Bets/No. QC', domain="[('product_id', '=', product_id)]", copy=False)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    move_id = fields.Many2one('stock.move')


# class MrpProductionPencampuran(models.Model):
#     _name = 'mrp.production.pencampuran'

#     production_id = fields.Many2one('mrp.production', ondelete='cascade')


# class MrpProductionFillingKapsul(models.Model):
#     _name = 'mrp.production.filling.kapsul'

#     production_id = fields.Many2one('mrp.production', ondelete='cascade')


# class MrpProductionFillingPrimer(models.Model):
#     _name = 'mrp.production.filling.primer'

#     production_id = fields.Many2one('mrp.production', ondelete='cascade') 