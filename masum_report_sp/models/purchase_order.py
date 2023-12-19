from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class AccountMoveInformation(models.Model):
    _name = 'account.move.information'
    _rec_name = 'informasi'

    informasi = fields.Text(string='informasi', store=True)
    user_signature = fields.Char(string='user', store=True)
    footer1 = fields.Text(string='Footer1', store=True)
    footer2 = fields.Text(string='Footer2', store=True)


class AccountMove(models.Model):
    _inherit = ['account.move']

    total_diskon = fields.Float(
        string=u'Total Diskon', compute='_get_total_diskon', store=True)
    user_signature = fields.Char(string='user',)
    footer1 = fields.Text(string='Footer', store=True)
    footer2 = fields.Text(string='Footer2', store=True)

    def _get_copy_data_narration(self):
        self.narration = self.account_move_information_id.informasi
        self.user_signature = self.account_move_information_id.user_signature
        self.footer1 = self.account_move_information_id.footer1
        self.footer2 = self.account_move_information_id.footer2

    @api.depends('invoice_line_ids')
    def _get_total_diskon(self):
        for move_id in self:
            move_id.total_diskon = sum(
                (line_id.sh_discounted_total_amount) for line_id in move_id.invoice_line_ids)
        self._get_copy_data_narration()

    # @api.model
    # def _default_account_move_information(self):
    #     return self.env['account.move.information'].search([('id', '=',206)],limit=1)

    account_move_information_id = fields.Many2one(
        'account.move.information', string='Account Move Information', store=True)


class AccountMove2(models.Model):
    _inherit = ['account.move']

    account_move_information_id = fields.Many2one(
        'account.move.information', string='Account Move Information', default=1, store=True)
