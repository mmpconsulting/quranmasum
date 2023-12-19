from odoo import models, fields, api


MO_TYPE = [
    ('olah', 'Olah'),
    ('kemas', 'Kemas')
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mo_type = fields.Selection(MO_TYPE, string="MO Type", default=False)
    filling_primer_ids = fields.One2many('filling.primer', 'product_tmpl_id')
    filling_kapsul_ids = fields.One2many('filling.kapsul', 'product_tmpl_id')
    pencampuran_ids = fields.One2many('pencampuran.pencampuran', 'product_tmpl_id')
    pengemasan_ids = fields.One2many('pengemasan.pengemasan', 'product_tmpl_id')
    pengawasan_ids = fields.One2many('pengawasan.pengawasan', 'product_tmpl_id')


class FillingPrimer(models.Model):
    _name = 'filling.primer'
    _description = 'Langkah Kerja Filling Primer'
    _rec_name = 'step'

    product_tmpl_id = fields.Many2one('product.template', ondelete='cascade')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')

    @api.model
    def default_get(self, default_fields):
        context = self._context
        res = super(FillingPrimer, self).default_get(default_fields)
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'filling_primer_ids' in context_keys:
                if len(context.get('filling_primer_ids')) > 0:
                    next_sequence = len(context.get('filling_primer_ids')) + 1
        res.update({'sequence': next_sequence})
        return res


class FillingKapsul(models.Model):
    _name = 'filling.kapsul'
    _description = 'Langkah Kerja Filling Kapsul'
    _rec_name = 'step'

    product_tmpl_id = fields.Many2one('product.template', ondelete='cascade')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')

    @api.model
    def default_get(self, default_fields):
        context = self._context
        res = super(FillingKapsul, self).default_get(default_fields)
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'filling_kapsul_ids' in context_keys:
                if len(context.get('filling_kapsul_ids')) > 0:
                    next_sequence = len(context.get('filling_kapsul_ids')) + 1
        res.update({'sequence': next_sequence})
        return res


class Pencampuran(models.Model):
    _name = 'pencampuran.pencampuran'
    _description = 'Langkah Kerja Pencampuran'
    _rec_name = 'step'

    product_tmpl_id = fields.Many2one('product.template', ondelete='cascade')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')

    @api.model
    def default_get(self, default_fields):
        context = self._context
        res = super(Pencampuran, self).default_get(default_fields)
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'pencampuran_ids' in context_keys:
                if len(context.get('pencampuran_ids')) > 0:
                    next_sequence = len(context.get('pencampuran_ids')) + 1
        res.update({'sequence': next_sequence})
        return res


class Pengemasan(models.Model):
    _name = 'pengemasan.pengemasan'
    _description = 'Langkah Kerja Pengemasan'
    _rec_name = 'step'

    product_tmpl_id = fields.Many2one('product.template', ondelete='cascade')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')

    @api.model
    def default_get(self, default_fields):
        context = self._context
        res = super(Pengemasan, self).default_get(default_fields)
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'pengemasan_ids' in context_keys:
                if len(context.get('pengemasan_ids')) > 0:
                    next_sequence = len(context.get('pengemasan_ids')) + 1
        res.update({'sequence': next_sequence})
        return res


class Pengawasan(models.Model):
    _name = 'pengawasan.pengawasan'
    _description = 'Langkah Kerja Pengawasan'
    _rec_name = 'step'

    product_tmpl_id = fields.Many2one('product.template', ondelete='cascade')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')

    @api.model
    def default_get(self, default_fields):
        context = self._context
        res = super(Pengawasan, self).default_get(default_fields)
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'pengawasan_ids' in context_keys:
                if len(context.get('pengawasan_ids')) > 0:
                    next_sequence = len(context.get('pengawasan_ids')) + 1
        res.update({'sequence': next_sequence})
        return res