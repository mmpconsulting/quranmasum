from odoo import models, fields, api
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    line_per_page = fields.Integer(string='Lines per Page', default="12")
    footer_note = fields.Html(stirng="Footer Notes", default="<strong>Pembayaran: </strong><br/><span>Maksum Media Berkah </span><br/><span>Bank  : BCA </span><br/><span>AC      : 785 1015993 </span>")

    