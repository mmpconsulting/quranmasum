from odoo import models, fields, api
from odoo.addons.cpk_cpb.models.mrp_production import PENGOLAHAN_STATE_ORDER, PENGEMASAN_STATE_ORDER


class MrpProductionEvaluasi(models.Model):
    _name = 'mrp.production.evaluasi'
    _description = 'MRP Production Evaluasi'

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionEvaluasi, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            if 'production_id' in fields:
                res['production_id'] = production.id
            if self._context.get('evaluation_type'):
                res['type'] = self._context.get('evaluation_type')
        return res

    production_id = fields.Many2one('mrp.production', ondelete='cascade')
    type = fields.Selection([('pengolahan', 'Pengolahan'), ('pengemasan', 'Pengemasan')])

    date_hasil_produksi = fields.Date()
    date_hasil_qc = fields.Date()
    
    ka_produksi = fields.Many2one('res.users')
    ka_qc = fields.Many2one('res.users')

    @api.model
    def create(self, vals):
        obj = super(MrpProductionEvaluasi, self).create(vals)
        values = {'evaluasi_{}_id'.format(obj.type): obj.id}
        obj.production_id.write(values)
        return obj 

    @api.multi
    def write(self, vals):
        res = super(MrpProductionEvaluasi, self).write(vals)
        for rec in self:
            if rec.type == 'pengolahan':
                if not rec.production_id.evaluasi_pengolahan_id:
                    rec.production_id.write({
                        'evaluasi_pengolahan_id': rec.id
                    })
            elif rec.type == 'pengemasan':
                if not rec.production_id.evaluasi_pengemasan_id:
                    rec.production_id.write({
                        'evaluasi_pengemasan_id': rec.id
                    })
        return res

    @api.multi
    def confirm(self):
        self.ensure_one()
        if self.type == 'pengolahan':
            self.production_id.change_state(PENGOLAHAN_STATE_ORDER)
        elif self.type == 'pengemasan':
            self.production_id.change_state(PENGEMASAN_STATE_ORDER)
        return {'type': 'ir.actions.act_window_close'}