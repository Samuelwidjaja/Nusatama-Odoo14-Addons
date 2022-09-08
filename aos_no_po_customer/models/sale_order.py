"""
- sale.order
"""
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'




    no_po = fields.Char(string="No Pesanan")