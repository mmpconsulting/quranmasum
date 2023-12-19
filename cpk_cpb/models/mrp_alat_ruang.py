from email.policy import default
from odoo import fields, models, api


CATEGORY = [
    ('alat', 'Alat'),
    ('ruang', 'Ruang'),
    ('dll', 'Lainnya')
]


class MrpAlatRuang(models.Model):
    _name = 'mrp.alat.ruang'
    _description = "MRP Alat dan Ruang"

    name = fields.Char('Name')
    code = fields.Char('Code')
    active = fields.Boolean('Active', default=True, copy=False)
    protap_ids = fields.One2many('protap.protap', 'alat_ruang_id')
    category = fields.Selection(CATEGORY, default=False)

    def action_open_alat_ruang(self):
        action = self.env.ref('cpk_cpb.mrp_production_smart_button_action').read()[0]
        if self.category == 'alat':
            action['domain'] = [('alat_ids.alat_id', '=', self.id)]
        elif self.category == 'ruang':
            action['domain'] = [('ruang_ids.ruang_id', '=', self.id)]
        action['context'] = {}
        return action


class Protap(models.Model):
    _name = 'protap.protap'
    _description = 'Protap'

    alat_ruang_id = fields.Many2one('mrp.alat.ruang', ondelete='cascade')
    name = fields.Char('No Dokumen')
    file = fields.Binary('Protap Dokumen')

    @api.depends('name')
    def _get_filename(self):
        for rec in self:
            if rec.name:
                rec.filename = "%s" % rec.name
            else:
                rec.filename = False

    filename = fields.Char('Filename', compute='_get_filename', store=True)