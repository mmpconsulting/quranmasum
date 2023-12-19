from odoo import models, fields, api, _
from odoo.addons.cpk_cpb.models.mrp_production import PENGEMASAN_STATE_ORDER
from odoo.exceptions import UserError


class MrpProductionRekonsiliasiPengemasan(models.Model):
    _name = 'mrp.production.rekonsiliasi.pengemasan'
    _description = 'MRP Production Rekonsiliasi Pengemasan'

    pelaksana = fields.Many2one('res.users')
    pemeriksa = fields.Many2one('res.users')

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionRekonsiliasiPengemasan, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            if 'production_id' in fields:
                res['production_id'] = production.id

            raw_rekonsiliasi_bahan_kemas = []
            if production.mo_type == 'olah':
                move_raw_ids = production.move_raw_bahan_pengemas_ids
            elif production.mo_type == 'kemas':
                move_raw_ids = production.move_raw_bahan_kemas_sekunder_ids
            else:
                raise UserError(__('Tolong isi mo_type di master data produk'))
            for move in move_raw_ids:
                raw_rekonsiliasi_bahan_kemas.append((0, False, {
                    'product_id': move.product_id.id,
                    'jumlah_teoritis_per_bets': move.product_uom_qty,
                    'jumlah_teoritis_per_order': float(move.product_uom_qty / production.product_qty),
                    'product_uom': move.product_uom.id,
                    'move_id': move.id
                }))
            if raw_rekonsiliasi_bahan_kemas:
                res['rekonsiliasi_bahan_kemas_ids'] = raw_rekonsiliasi_bahan_kemas
        return res

    production_id = fields.Many2one('mrp.production', ondelete='cascade')

    rekonsiliasi_bahan_kemas_ids = fields.One2many('mrp.production.rekonsiliasi.bahan.kemas', 'rekonsiliasi_id')

    box_penuh_ids = fields.One2many('mrp.production.rekonsiliasi.box.penuh', 'rekonsiliasi_id')
    box_tidak_penuh = fields.Float('Box tidak penuh')
    jumlah_botol = fields.Integer('Jumlah botol')

    @api.model
    def create(self, vals):
        obj = super(MrpProductionRekonsiliasiPengemasan, self).create(vals)
        obj.production_id.write({
            'rekonsiliasi_id': obj.id
        })
        return obj 

    @api.multi
    def write(self, vals):
        res = super(MrpProductionRekonsiliasiPengemasan, self).write(vals)
        for rec in self:
            if not rec.production_id.rekonsiliasi_id:
                rec.production_id.write({
                    'rekonsiliasi_id': rec.id
                })
        return res

    @api.multi
    def confirm(self):
        self.ensure_one()
        self.production_id.change_state(PENGEMASAN_STATE_ORDER)
        return {'type': 'ir.actions.act_window_close'}

    total_hasil_pengemasan = fields.Float('Total hasil pengemasan')
    total_hasil_produk_jadi = fields.Float('Total hasil produk jadi')

    @api.depends('total_hasil_pengemasan', 'total_hasil_produk_jadi')
    def _compute_persentase_hasil(self):
        for rec in self:
            if rec.total_hasil_produk_jadi > 0:
                rec.persentase_hasil = float((rec.total_hasil_pengemasan * 100.0) / rec.total_hasil_produk_jadi)
            else:
                rec.persentase_hasil = 0.0

    persentase_hasil = fields.Float(compute='_compute_persentase_hasil')
    batas_hasil_min = fields.Float('Batas Hasil Min', default=94.0)
    batas_hasil_max = fields.Float('Batas Hasil Max', default=105.0)

    @api.depends('batas_hasil_min', 'batas_hasil_max', 'persentase_hasil')
    def _compute_status(self):
        for rec in self:
            if rec.persentase_hasil >= rec.batas_hasil_min and rec.persentase_hasil <= rec.batas_hasil_max:
                rec.status = 'ok'
            else:
                rec.status = 'not_ok'

    status = fields.Selection([('ok', 'OK'), ('not_ok', 'NOT OK')], compute='_compute_status')


class MrpProductionRekonsiliasiBahanKemas(models.Model):
    _name = 'mrp.production.rekonsiliasi.bahan.kemas'
    _description = 'MRP Production Rekonsiliasi Bahan Kemas'

    rekonsiliasi_id = fields.Many2one('mrp.production.rekonsiliasi.pengemasan', ondelete='cascade')

    product_id = fields.Many2one('product.product', copy=False, required=True)
    jumlah_teoritis_per_bets = fields.Float('Kebutuhan Teoritis per Bets', copy=False)
    jumlah_teoritis_per_order = fields.Float('Kebutuhan Teoritis per Order', copy=False)
    diterima = fields.Float('Diterima', copy=False)
    dipakai = fields.Float('Dipakai', copy=False)
    rusak = fields.Float('Rusak', copy=False)
    dikembalikan = fields.Float('Dikembalikan', copy=False)
    dihancurkan = fields.Float('Dihancurkan', copy=False)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    move_id = fields.Many2one('stock.move')


class MrpProductionRekonsiliasiBoxPenuh(models.Model):
    _name = 'mrp.production.rekonsiliasi.box.penuh'
    _description = 'MRP Production Rekonsiliasi Box Penuh'

    rekonsiliasi_id = fields.Many2one('mrp.production.rekonsiliasi.pengemasan', ondelete='cascade')

    date = fields.Date('Tanggal')
    quantity = fields.Float('Kuantitas')