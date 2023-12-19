from odoo import models, fields, api
from odoo.addons.cpk_cpb.models.mrp_production import PENGOLAHAN_STATE_ORDER


class MrpProductionFillingPrimer(models.Model):
    _name = 'mrp.production.filling.primer'
    _description = 'MRP Production Filling Primer'

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionFillingPrimer, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            if 'production_id' in fields:
                res['production_id'] = production.id

                # add step filling Primer based on product_tmpl_id
                if production.product_tmpl_id:
                    steps = []
                    step_ids = self.env['filling.primer'].search([('product_tmpl_id', '=', production.product_tmpl_id.id)], order='sequence asc')
                    for step_id in step_ids:
                        steps.append((0, False, {
                            'sequence': step_id.sequence,
                            'step': step_id.step,
                            'product_tmpl_id': production.product_tmpl_id.id
                        }))
                    if steps:
                        res['step_filling_primer_ids'] = steps

                # add stock move rekonsiliasi
                raw_rekonsiliasi = []
                for move in production.move_raw_bahan_pengemas_ids:
                    raw_rekonsiliasi.append((0, False, {
                        'product_id': move.product_id.id,
                        'jumlah_teoritis': move.product_uom_qty,
                        'product_uom': move.product_uom.id,
                        'move_id': move.id
                    }))
                if raw_rekonsiliasi:
                    res['rekonsiliasi_move_ids'] = raw_rekonsiliasi
        return res

    production_id = fields.Many2one('mrp.production', ondelete='cascade')

    date = fields.Datetime()
    product_id = fields.Many2one('product.product')
    nomor_bets = fields.Many2one('stock.production.lot', domain="[('product_id', '=', product_id)]", copy=False)
    pelaksana = fields.Many2one('res.users')
    pemeriksa = fields.Many2one('res.users')
    
    step_filling_primer_ids = fields.One2many('mrp.production.filling.primer.step', 'filling_primer_id')
    rekonsiliasi_move_ids = fields.One2many('stock.move.rekonsiliasi.pengemas', 'filling_primer_id')

    @api.model
    def create(self, vals):
        obj = super(MrpProductionFillingPrimer, self).create(vals)
        obj.production_id.write({
            'filling_primer_id': obj.id
        })
        return obj 

    @api.multi
    def write(self, vals):
        res = super(MrpProductionFillingPrimer, self).write(vals)
        for rec in self:
            if not rec.production_id.filling_primer_id:
                rec.production_id.write({
                    'filling_primer_id': rec.id
                })
        return res

    @api.multi
    def confirm(self):
        self.ensure_one()
        self.production_id.change_state(PENGOLAHAN_STATE_ORDER)
        return {'type': 'ir.actions.act_window_close'}

    # deviasi ------------------------------------
    deviasi_hasil_teoritis = fields.Float('Hasil Teoritis')
    deviasi_hasil_nyata = fields.Float('Hasil Nyata')

    @api.depends('deviasi_hasil_teoritis', 'deviasi_hasil_nyata')
    def _compute_deviasi_keterangan(self):
        for rec in self:
            if not rec.deviasi_hasil_teoritis:
                rec.deviasi_keterangan = '1'
                continue
            result = (abs(rec.deviasi_hasil_teoritis - rec.deviasi_hasil_nyata) / rec.deviasi_hasil_teoritis) * 100
            if result > 10:
                rec.deviasi_keterangan = '0'
            else:
                rec.deviasi_keterangan = '1'

    deviasi_keterangan = fields.Selection([('1', 'OK'), ('0', 'NOT OK')], compute='_compute_deviasi_keterangan')

    # rekonsiliasi pembotolan --------------------

    hasil = fields.Float('Hasil (a)')
    nyata = fields.Float('Nyata (b)')
    sampel_qc = fields.Float('Sampel QC (c)')
    rusak = fields.Float('Rusak (d)')
    batas_hasil_min = fields.Float('Batas Hasil Min', default=95.0)
    batas_hasil_max = fields.Float('Batas Hasil Max', default=105.0)

    @api.depends('hasil', 'nyata', 'sampel_qc', 'rusak')
    def _compute_rekonsiliasi_pembotolan(self):
        for rec in self:
            if rec.hasil > 0:
                result = round(float(((rec.nyata + rec.sampel_qc + rec.rusak) * 100.0 ) / rec.hasil), 2)
            else:
                result = 0.0
            rec.rekonsiliasi_pembotolan = result

    rekonsiliasi_pembotolan = fields.Float(string='Rekonsiliasi', compute='_compute_rekonsiliasi_pembotolan', store=True)
    
    @api.depends('batas_hasil_min', 'batas_hasil_max', 'rekonsiliasi_pembotolan')
    def _compute_status_rekonsiliasi_pembotolan(self):
        for rec in self:
            if rec.rekonsiliasi_pembotolan >= rec.batas_hasil_min and rec.rekonsiliasi_pembotolan <= rec.batas_hasil_max:
                rec.status_rekonsiliasi_pembotolan = '1'
            else:
                rec.status_rekonsiliasi_pembotolan = '0'

    status_rekonsiliasi_pembotolan = fields.Selection([('1', 'OK'), ('0', 'NOT OK')], compute='_compute_status_rekonsiliasi_pembotolan')

class MrpProductionFillingPrimerStep(models.Model):
    _name = 'mrp.production.filling.primer.step'
    _description = 'MRP Production Filling Primer Step'

    filling_primer_id = fields.Many2one('mrp.production.filling.primer', ondelete='cascade')

    product_tmpl_id = fields.Many2one('product.template')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')


class StockMoveRekonsiliasiPengemas(models.Model):
    _name = 'stock.move.rekonsiliasi.pengemas'
    _description = 'Stock Move Rekonsiliasi Pengemas'

    filling_primer_id = fields.Many2one('mrp.production.filling.primer', ondelete='cascade')

    product_id = fields.Many2one('product.product', copy=False, required=True)
    jumlah_teoritis = fields.Float('Jumlah Teoritis', copy=False)
    diterima = fields.Float('Diterima', copy=False)
    dipakai = fields.Float('Dipakai', copy=False)
    rusak = fields.Float('Rusak', copy=False)
    dikembalikan = fields.Float('Dikembalikan', copy=False)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True, copy=False)
    move_id = fields.Many2one('stock.move', copy=False)