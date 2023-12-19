from cmath import log
from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
import json
from ast import literal_eval


CUSTOM_PRODUCTION_STATES = [
    ('confirmed', 'Confirmed'),
    ('planned', 'Planned'),
    ('penimbangan', 'Penimbangan'),
    ('pencampuran', 'Pencampuran'),
    ('filling_kapsul', 'Filling Kapsul'),
    ('filling_primer', 'Filling Primer'),
    ('prosedur', 'Prosedur'),
    ('pengawasan', 'Pengawasan'),
    ('rekonsiliasi', 'Rekonsiliasi'),
    ('evaluasi_olah', 'Evaluasi'),
    ('evaluasi_kemas', 'Evaluasi'),
    ('progress', 'In Progress'),
    ('done', 'Done'),
    ('cancel', 'Cancelled')
]

PENGOLAHAN_STATE_ORDER = ['penimbangan', 'pencampuran', 'filling_kapsul', 'filling_primer', 'progress', 'evaluasi_olah']
PENGEMASAN_STATE_ORDER = ['prosedur', 'pengawasan', 'rekonsiliasi', 'progress', 'evaluasi_kemas']

# bisa dimasukkan ke setting/configuration
BAHAN_AWAL_CATEG_NAME = ['All / Consumable']
BAHAN_PENGEMAS_CATEG_NAME = ['All / Saleable / Office Furniture']

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mo_type = fields.Selection(related='product_id.product_tmpl_id.mo_type')

    alat_ids = fields.One2many('mrp.production.alat', 'production_id')
    ruang_ids = fields.One2many('mrp.production.ruang', 'production_id')

    state = fields.Selection(CUSTOM_PRODUCTION_STATES, string='State', copy=False, default='confirmed', track_visibility='onchange')

    protap_penyimpangan_id = fields.Many2one('protap.protap', domain="[('alat_ruang_id.category', '=', 'dll')]", copy=False)
    penimbangan_id = fields.Many2one('mrp.production.penimbangan', copy=False)
    pencampuran_id = fields.Many2one('mrp.production.pencampuran', copy=False)
    filling_kapsul_id = fields.Many2one('mrp.production.filling.kapsul', copy=False)
    filling_primer_id = fields.Many2one('mrp.production.filling.primer', copy=False)
    evaluasi_pengolahan_id = fields.Many2one('mrp.production.evaluasi', copy=False)
    evaluasi_pengemasan_id = fields.Many2one('mrp.production.evaluasi', copy=False)
    pengemasan_id = fields.Many2one('mrp.production.prosedur.pengemasan', copy=False)
    pengawasan_id = fields.Many2one('mrp.production.pengawasan.pengemasan', copy=False)
    rekonsiliasi_id = fields.Many2one('mrp.production.rekonsiliasi.pengemasan', copy=False)
    ka_produksi = fields.Many2one('res.users', copy=False)
    date_mo = fields.Date()
    date_mulai = fields.Date()
    date_selesai = fields.Date()

    @api.depends('move_raw_ids')
    def _compute_move_raw_bahan_awal(self):
        categ_bahan_awal_ids = literal_eval(self.env['ir.config_parameter'].sudo().get_param('cpk_cpb.default_categ_bahan_awal', '[]'))
        for rec in self:
            move_raw_ids = rec.move_raw_ids.filtered(lambda x: x.product_id.categ_id.id in categ_bahan_awal_ids).ids
            rec.move_raw_bahan_awal_ids = [(6, 0, move_raw_ids)]

    @api.depends('move_raw_ids')
    def _compute_move_raw_bahan_pengemas(self):
        categ_bahan_pengemas_ids = literal_eval(self.env['ir.config_parameter'].sudo().get_param('cpk_cpb.default_categ_bahan_pengemas', '[]'))
        for rec in self:
            move_raw_ids = rec.move_raw_ids.filtered(lambda x: x.product_id.categ_id.id in categ_bahan_pengemas_ids).ids
            rec.move_raw_bahan_pengemas_ids = [(6, 0, move_raw_ids)]

    @api.depends('move_raw_ids')
    def _compute_move_raw_bahan_kemas_sekunder(self):
        categ_bahan_kemas_sekunder_ids = literal_eval(self.env['ir.config_parameter'].sudo().get_param('cpk_cpb.default_categ_bahan_kemas_sekunder', '[]'))
        for rec in self:
            move_raw_ids = rec.move_raw_ids.filtered(lambda x: x.product_id.categ_id.id in categ_bahan_kemas_sekunder_ids).ids
            rec.move_raw_bahan_kemas_sekunder_ids = [(6, 0, move_raw_ids)]

    move_raw_bahan_awal_ids = fields.Many2many('stock.move', 'mrp_move_raw_bahan_awal_rel', 'move_id', 'production_id', compute='_compute_move_raw_bahan_awal', store=True)
    move_raw_bahan_pengemas_ids = fields.Many2many('stock.move', 'mrp_move_raw_bahan_pengemas_rel', 'move_id', 'production_id', compute='_compute_move_raw_bahan_pengemas', store=True)
    move_raw_bahan_kemas_sekunder_ids = fields.Many2many('stock.move', 'mrp_move_raw_bahan_kemas_sekunder_rel', 'move_id', 'production_id', compute='_compute_move_raw_bahan_kemas_sekunder', store=True)

    @api.multi
    def do_start_process(self):
        self.ensure_one()
        if self.mo_type == 'olah':
            self.state = PENGOLAHAN_STATE_ORDER[0]
        elif self.mo_type == 'kemas':
            self.state = PENGEMASAN_STATE_ORDER[0]
        return True

    @api.multi
    def do_penimbangan(self):
        self.ensure_one()
        action = self.env.ref('cpk_cpb.act_mrp_production_penimbangan').read()[0]
        penimbangan_id = self.env[action['res_model']].search([('production_id', '=', self.id)])
        action['res_id'] = penimbangan_id.id
        return action

    @api.multi
    def do_pencampuran(self):
        self.ensure_one()
        action = self.env.ref('cpk_cpb.act_mrp_production_pencampuran').read()[0]
        pencampuran_id = self.env[action['res_model']].search([('production_id', '=', self.id)])
        action['res_id'] = pencampuran_id.id
        return action

    @api.multi
    def do_filling_kapsul(self):
        self.ensure_one()
        action = self.env.ref('cpk_cpb.act_mrp_production_filling_kapsul').read()[0]
        filling_kapsul_id = self.env[action['res_model']].search([('production_id', '=', self.id)])
        action['res_id'] = filling_kapsul_id.id
        return action

    @api.multi
    def do_filling_primer(self):
        self.ensure_one()
        action = self.env.ref('cpk_cpb.act_mrp_production_filling_primer').read()[0]
        filling_primer_id = self.env[action['res_model']].search([('production_id', '=', self.id)])
        action['res_id'] = filling_primer_id.id
        return action

    @api.multi
    def do_evaluasi_pengolahan(self):
        self.ensure_one()
        action = self.env.ref('cpk_cpb.act_mrp_production_evaluasi').read()[0]
        evaluasi_id = self.env[action['res_model']].search([('production_id', '=', self.id), ('type', '=', 'pengolahan')])
        action['res_id'] = evaluasi_id.id
        if action['context']:
            action['context'] = dict(action['context'], evaluation_type='pengolahan')
        else:
            action['context'] = dict(evaluation_type='pengolahan')
        return action

    @api.multi
    def do_evaluasi_pengemasan(self):
        self.ensure_one()
        action = self.env.ref('cpk_cpb.act_mrp_production_evaluasi').read()[0]
        evaluasi_id = self.env[action['res_model']].search([('production_id', '=', self.id), ('type', '=', 'pengemasan')])
        action['res_id'] = evaluasi_id.id
        action['context'] = dict(action['context'], evaluation_type='pengemasan')
        return action

    @api.multi
    def do_prosedur(self):
        self.ensure_one()
        action = self.env.ref('cpk_cpb.act_mrp_production_prosedur_pengemasan').read()[0]
        filling_primer_id = self.env[action['res_model']].search([('production_id', '=', self.id)])
        action['res_id'] = filling_primer_id.id
        return action

    @api.multi
    def do_pengawasan(self):
        self.ensure_one()
        action = self.env.ref('cpk_cpb.act_mrp_production_pengawasan_pengemasan').read()[0]
        filling_primer_id = self.env[action['res_model']].search([('production_id', '=', self.id)])
        action['res_id'] = filling_primer_id.id
        return action

    @api.multi
    def do_rekonsiliasi(self):
        self.ensure_one()
        action = self.env.ref('cpk_cpb.act_mrp_production_rekonsiliasi_pengemasan').read()[0]
        filling_primer_id = self.env[action['res_model']].search([('production_id', '=', self.id)])
        action['res_id'] = filling_primer_id.id
        return action

    def change_state(self, params=None):
        self.ensure_one()
        do_loop = False
        if not params:
            do_loop = True
        if not params or isinstance(params, dict):
            if isinstance(params, dict) and params.get('params'):
                do_loop = True
            # params = [line[0] for line in CUSTOM_PRODUCTION_STATES if line[0] not in ('planned', 'cancel')]
            if self.mo_type == 'olah':
                CUSTOM_STATES = PENGOLAHAN_STATE_ORDER
            elif self.mo_type == 'kemas':
                CUSTOM_STATES = PENGEMASAN_STATE_ORDER
            else:
                raise UserError(_('mo type not found'))
            params = [line for line in CUSTOM_STATES if line not in ('planned', 'cancel')]
        idx = params.index(self.state) + 1
        logging.info(idx)
        logging.info(params)
        if idx == len(params):
            idx = 0
            if not do_loop:
                # jika indek terakhir, jangan diulang state penimbangan
                return
        for rec in self:
            rec.state = params[idx]
        return


class MrpProductionAlat(models.Model):
    _name = 'mrp.production.alat'
    _description = 'MRP Production Alat'
    _rec_name = 'full_name'

    _sql_constraints = [('mrp_production_alat_uniq', 'unique (production_id,alat_id)',     
                 'Ada Duplikasi Alat')]

    production_id = fields.Many2one('mrp.production', ondelete='cascade')
    sequence = fields.Integer('Nomor')
    alat_id = fields.Many2one('mrp.alat.ruang')
    protap_id = fields.Many2one('protap.protap')
    full_name = fields.Char(compute='_compute_full_name')

    @api.depends('alat_id', 'protap_id')
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = '[{}] {}'.format(rec.protap_id.name, rec.alat_id.name)

    @api.model
    def default_get(self, default_fields):
        context = self._context
        res = super(MrpProductionAlat, self).default_get(default_fields)
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'alat_ids' in context_keys:
                if len(context.get('alat_ids')) > 0:
                    next_sequence = len(context.get('alat_ids')) + 1
        res.update({'sequence': next_sequence})
        return res


class MrpProductionRuang(models.Model):
    _name = 'mrp.production.ruang'
    _description = 'MRP Production Ruang'
    _rec_name = 'full_name'

    _sql_constraints = [('mrp_production_ruang_uniq', 'unique (production_id,ruang_id)',     
                 'Ada Duplikasi Ruang')]

    production_id = fields.Many2one('mrp.production', ondelete='cascade')
    sequence = fields.Integer('Nomor')
    ruang_id = fields.Many2one('mrp.alat.ruang')
    protap_id = fields.Many2one('protap.protap')
    full_name = fields.Char(compute='_compute_full_name')

    @api.depends('ruang_id', 'protap_id')
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = '[{}] {}'.format(rec.protap_id.name, rec.ruang_id.name)


    @api.model
    def default_get(self, default_fields):
        context = self._context
        res = super(MrpProductionRuang, self).default_get(default_fields)
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'ruang_ids' in context_keys:
                if len(context.get('ruang_ids')) > 0:
                    next_sequence = len(context.get('ruang_ids')) + 1
        res.update({'sequence': next_sequence})
        return res
