from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def is_delivery_product(self):
        self.env.cr.execute("select * from delivery_carrier where product_id = " + str(self.id))
        res = self.env.cr.dictfetchall() or False 

        if res:
            return True
        else: 
            return False

        

    