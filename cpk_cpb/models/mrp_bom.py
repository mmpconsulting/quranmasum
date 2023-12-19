from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from werkzeug.urls import url_encode
import logging

class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    jumlah_kapsul = fields.Integer(string='Jumlah Kapsul', copy=True)
