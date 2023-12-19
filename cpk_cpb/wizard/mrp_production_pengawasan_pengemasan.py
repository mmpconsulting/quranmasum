from odoo import models, fields, api
from odoo.addons.cpk_cpb.models.mrp_production import PENGEMASAN_STATE_ORDER


class MrpProductionPengawasanPengemasan(models.Model):
    _name = 'mrp.production.pengawasan.pengemasan'
    _description = 'MRP Production Prosedur'

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionPengawasanPengemasan, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            if 'production_id' in fields:
                res['production_id'] = production.id

                # add step pengawasan based on product_tmpl_id
                if production.product_tmpl_id:
                    steps = []
                    pengawasan_step_ids = self.env['pengawasan.pengawasan'].search([('product_tmpl_id', '=', production.product_tmpl_id.id)], order='sequence asc')
                    for step_id in pengawasan_step_ids:
                        steps.append((0, False, {
                            'sequence': step_id.sequence,
                            'step': step_id.step,
                            'product_tmpl_id': production.product_tmpl_id.id
                        }))
                    if steps:
                        res['step_pengawasan_ids'] = steps
        return res

    production_id = fields.Many2one('mrp.production', ondelete='cascade')
    
    step_pengawasan_ids = fields.One2many('mrp.production.pengawasan.pengemasan.step', 'pengawasan_id')

    @api.model
    def create(self, vals):
        obj = super(MrpProductionPengawasanPengemasan, self).create(vals)
        obj.production_id.write({
            'pengawasan_id': obj.id
        })
        return obj 

    @api.multi
    def write(self, vals):
        res = super(MrpProductionPengawasanPengemasan, self).write(vals)
        for rec in self:
            if not rec.production_id.pengawasan_id:
                rec.production_id.write({
                    'pengawasan_id': rec.id
                })
        return res

    @api.multi
    def confirm(self):
        self.ensure_one()
        self.production_id.change_state(PENGEMASAN_STATE_ORDER)
        return {'type': 'ir.actions.act_window_close'}


class MrpProductionPengawasanPengemasanStep(models.Model):
    _name = 'mrp.production.pengawasan.pengemasan.step'
    _description = 'MRP Production Prosedur Pengemasan Step'

    pengawasan_id = fields.Many2one('mrp.production.pengawasan.pengemasan', ondelete='cascade')

    product_tmpl_id = fields.Many2one('product.template')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')

    keterangan = fields.Text('Keterangan')