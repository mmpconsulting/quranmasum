from odoo import models, fields, api
from odoo.addons.cpk_cpb.models.mrp_production import PENGOLAHAN_STATE_ORDER


class MrpProductionFillingKapsul(models.Model):
    _name = 'mrp.production.filling.kapsul'
    _description = 'MRP Production Filling Kapsul'

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionFillingKapsul, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            if 'production_id' in fields:
                res['production_id'] = production.id

                # add step filling kapsul based on product_tmpl_id
                if production.product_tmpl_id:
                    steps = []
                    step_ids = self.env['filling.kapsul'].search([('product_tmpl_id', '=', production.product_tmpl_id.id)], order='sequence asc')
                    for step_id in step_ids:
                        steps.append((0, False, {
                            'sequence': step_id.sequence,
                            'step': step_id.step,
                            'product_tmpl_id': production.product_tmpl_id.id
                        }))
                    if steps:
                        res['step_filling_kapsul_ids'] = steps
        return res

    def _default_jumlah_kapsul(self):
        return (self.production_id.product_qty)*(self.production_id.bom_id.jumlah_kapsul)

    production_id = fields.Many2one('mrp.production', ondelete='cascade')

    date = fields.Datetime()
    product_id = fields.Many2one('product.product')
    nomor_bets = fields.Many2one('stock.production.lot', domain="[('product_id', '=', product_id)]", copy=False)
    jumlah_kapsul = fields.Integer('Jumlah Kapsul', default=_default_jumlah_kapsul)
    pelaksana = fields.Many2one('res.users')
    pemeriksa = fields.Many2one('res.users')
    
    step_filling_kapsul_ids = fields.One2many('mrp.production.filling.kapsul.step', 'filling_kapsul_id')

    @api.model
    def create(self, vals):
        obj = super(MrpProductionFillingKapsul, self).create(vals)
        obj.production_id.write({
            'filling_kapsul_id': obj.id
        })
        return obj 

    @api.multi
    def write(self, vals):
        res = super(MrpProductionFillingKapsul, self).write(vals)
        for rec in self:
            if not rec.production_id.filling_kapsul_id:
                rec.production_id.write({
                    'filling_kapsul_id': rec.id
                })
        return res

    @api.multi
    def confirm(self):
        self.ensure_one()
        self.production_id.change_state(PENGOLAHAN_STATE_ORDER)
        return {'type': 'ir.actions.act_window_close'}


class MrpProductionFillingKapsulStep(models.Model):
    _name = 'mrp.production.filling.kapsul.step'
    _description = 'MRP Production Filling Kapsul Step'

    filling_kapsul_id = fields.Many2one('mrp.production.filling.kapsul', ondelete='cascade')

    product_tmpl_id = fields.Many2one('product.template')
    sequence = fields.Integer('Nomor')
    step = fields.Text('Langkah Kerja')