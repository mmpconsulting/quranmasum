from odoo import models, fields, api
from odoo.addons.cpk_cpb.models.mrp_production import PENGOLAHAN_STATE_ORDER


class MrpProductionPencampuran(models.Model):
    _name = 'mrp.production.pencampuran'
    _description = 'MRP Production Pencampuran'

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionPencampuran, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            if 'production_id' in fields:
                res['production_id'] = production.id

                # add step pencampuran based on product_tmpl_id
                if production.product_tmpl_id:
                    steps = []
                    pencampuran_step_ids = self.env['pencampuran.pencampuran'].search([('product_tmpl_id', '=', production.product_tmpl_id.id)], order='sequence asc')
                    for step_id in pencampuran_step_ids:
                        steps.append((0, False, {
                            'sequence': step_id.sequence,
                            'step': step_id.step,
                            'product_tmpl_id': production.product_tmpl_id.id
                        }))
                    if steps:
                        res['step_pencampuran_ids'] = steps
        return res

    production_id = fields.Many2one('mrp.production', ondelete='cascade')

    date = fields.Datetime()
    
    step_pencampuran_ids = fields.One2many('mrp.production.pencampuran.step', 'pencampuran_id')

    @api.model
    def create(self, vals):
        obj = super(MrpProductionPencampuran, self).create(vals)
        obj.production_id.write({
            'pencampuran_id': obj.id
        })
        return obj 

    @api.multi
    def write(self, vals):
        res = super(MrpProductionPencampuran, self).write(vals)
        for rec in self:
            if not rec.production_id.pencampuran_id:
                rec.production_id.write({
                    'pencampuran_id': rec.id
                })
        return res

    @api.multi
    def confirm(self):
        self.ensure_one()
        self.production_id.change_state(PENGOLAHAN_STATE_ORDER)
        return {'type': 'ir.actions.act_window_close'}


class MrpProductionPencampuranStep(models.Model):
    _name = 'mrp.production.pencampuran.step'
    _description = 'MRP Production Pencampuran Step'

    pencampuran_id = fields.Many2one('mrp.production.pencampuran', ondelete='cascade')

    product_tmpl_id = fields.Many2one('product.template')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')

    pelaksana = fields.Many2one('res.users')
    pemeriksa = fields.Many2one('res.users')