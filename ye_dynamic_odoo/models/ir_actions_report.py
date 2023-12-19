from odoo import models, api, fields


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def render_qweb_html(self, docids, data=None):
        return super(IrActionsReport, self.with_context(REPORT_ID=self.id)).render_qweb_html(docids, data=data)

