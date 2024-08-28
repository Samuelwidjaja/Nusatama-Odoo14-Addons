"""
- sale.order
"""
from odoo import models, fields,api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'




    no_po = fields.Char(string="Customer PO Number",required=False)


    def action_confirm(self):
        if not self.no_po:
            raise UserError("Customer PO Number  is required and cannot empty")

        return super(SaleOrder,self).action_confirm()
