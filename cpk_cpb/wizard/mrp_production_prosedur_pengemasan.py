from odoo import models, fields, api
from odoo.addons.cpk_cpb.models.mrp_production import PENGEMASAN_STATE_ORDER


class MrpProductionProsedurPengemasan(models.Model):
    _name = 'mrp.production.prosedur.pengemasan'
    _description = 'MRP Production Prosedur'

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionProsedurPengemasan, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            if 'production_id' in fields:
                res['production_id'] = production.id

                # add step pengemasan based on product_tmpl_id
                if production.product_tmpl_id:
                    steps = []
                    pengemasan_step_ids = self.env['pengemasan.pengemasan'].search([('product_tmpl_id', '=', production.product_tmpl_id.id)], order='sequence asc')
                    for step_id in pengemasan_step_ids:
                        steps.append((0, False, {
                            'sequence': step_id.sequence,
                            'step': step_id.step,
                            'product_tmpl_id': production.product_tmpl_id.id
                        }))
                    if steps:
                        res['step_pengemasan_ids'] = steps
        return res

    production_id = fields.Many2one('mrp.production', ondelete='cascade')

    date = fields.Datetime('Tanggal Kadaluarsa')
    
    step_pengemasan_ids = fields.One2many('mrp.production.prosedur.pengemasan.step', 'pengemasan_id')

    @api.model
    def create(self, vals):
        obj = super(MrpProductionProsedurPengemasan, self).create(vals)
        obj.production_id.write({
            'pengemasan_id': obj.id
        })
        return obj 

    @api.multi
    def write(self, vals):
        res = super(MrpProductionProsedurPengemasan, self).write(vals)
        for rec in self:
            if not rec.production_id.pengemasan_id:
                rec.production_id.write({
                    'pengemasan_id': rec.id
                })
        return res

    @api.multi
    def confirm(self):
        self.ensure_one()
        self.production_id.change_state(PENGEMASAN_STATE_ORDER)
        return {'type': 'ir.actions.act_window_close'}


class MrpProductionProsedurPengemasanStep(models.Model):
    _name = 'mrp.production.prosedur.pengemasan.step'
    _description = 'MRP Production Prosedur Pengemasan Step'

    pengemasan_id = fields.Many2one('mrp.production.prosedur.pengemasan', ondelete='cascade')

    product_tmpl_id = fields.Many2one('product.template')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')